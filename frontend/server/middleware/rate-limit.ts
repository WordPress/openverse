import { useRuntimeConfig } from "nitropack/runtime"
import {
  createError,
  defineEventHandler,
  getRequestHeader,
  getRequestURL,
  setResponseHeader,
} from "h3"
import { isInternalRequest } from "~~/server/utils/proxy"
import {
  getClientIp,
  getIpRateLimitKey,
  getRateLimitChecks,
  getRateLimitedRequestKind,
  RateLimiter,
  type RateLimitConfig,
} from "~~/server/utils/rate-limit"

import { ensureSession, getSessionConfig } from "#shared/utils/session"

let limiter: RateLimiter | null = null

/**
 * Writes one JSON line, so that CloudWatch Logs Insights reads its fields.
 * The logger formats objects over several lines, and each line becomes a
 * separate CloudWatch event. Writing to stdout directly also skips the
 * prefixes that a wrapped `console` adds.
 */
const logRateLimit = (event: string, fields: Record<string, unknown>) => {
  process.stdout.write(
    `${JSON.stringify({ log: "rate-limit", event, ...fields })}\n`
  )
}

const toRateLimitConfig = (
  config: Record<string, unknown>
): RateLimitConfig => ({
  mode: String(config.mode),
  windowSeconds: Number(config.windowSeconds),
  sessionLimit: Number(config.sessionLimit),
  noSessionLimit: Number(config.noSessionLimit),
  ipLimit: Number(config.ipLimit),
})

/**
 * Limits the proxy routes and the pages that call the API during SSR.
 * In `log` mode, it only logs the requests that would be limited. Session
 * values and IP addresses are never logged, only short hashes that change
 * with every Nuxt process.
 *
 * In-process SSR requests to the proxy routes are not counted, because their
 * page load is already counted.
 */
export default defineEventHandler(async (event) => {
  const kind = getRateLimitedRequestKind(getRequestURL(event).pathname)
  if (!kind || (kind === "api" && isInternalRequest(event))) {
    return
  }

  const runtimeConfig = useRuntimeConfig(event)
  const config = toRateLimitConfig(runtimeConfig.rateLimit)
  const enforce = config.mode === "enforce"
  limiter ??= new RateLimiter(config.windowSeconds * 1000, Date.now, (window) =>
    logRateLimit("window", { ...window, enforced: enforce })
  )

  const sessionConfig = getSessionConfig(
    runtimeConfig.hmacSigningSecret,
    runtimeConfig.public.deploymentEnv
  )
  // Before the limits, so that a limited response also renews the session.
  const session = sessionConfig
    ? await ensureSession(event, sessionConfig)
    : { id: null, state: "none" as const }

  const ip = getIpRateLimitKey(getClientIp(event))
  const result = limiter.hit(
    getRateLimitChecks({ kind, sessionId: session.id, ip, config })
  )
  if (!result) {
    return
  }

  if (result.isFirstExceeded) {
    logRateLimit("exceeded", {
      counter: result.counter,
      keyHash: result.keyHash,
      limit: result.limit,
      windowSeconds: config.windowSeconds,
      requestKind: kind,
      session: session.state,
      // Without any cookie, the browser may block cookies.
      hasCookies: Boolean(getRequestHeader(event, "cookie")),
      country: getRequestHeader(event, "cf-ipcountry") ?? null,
      enforced: enforce,
    })
  }
  if (!enforce) {
    return
  }

  setResponseHeader(event, "Retry-After", result.retryAfterSeconds)
  throw createError({
    statusCode: 429,
    statusMessage: "Too Many Requests",
    data: { retryAfter: result.retryAfterSeconds },
  })
})
