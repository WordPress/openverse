import { useNitroApp, useRuntimeConfig } from "nitropack/runtime"
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

import {
  getRequestSession,
  getSessionConfig,
  renewSession,
} from "#shared/utils/session"

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

/**
 * The exceeded windows are logged after they end. The timer logs them within
 * one more window on a task that gets no more requests, and the `close` hook
 * logs the open ones before the task stops.
 */
const createLimiter = (windowMs: number, enforced: boolean) => {
  const created = new RateLimiter(windowMs, Date.now, (window) =>
    logRateLimit("window", { ...window, enforced })
  )
  const timer = setInterval(() => created.prune(), windowMs)
  timer.unref()
  useNitroApp().hooks.hookOnce("close", () => {
    clearInterval(timer)
    created.flush()
  })
  return created
}

const toRateLimitConfig = (
  config: Record<string, unknown>
): RateLimitConfig => ({
  mode: String(config.mode),
  windowSeconds: Number(config.windowSeconds),
  sessionLimit: Number(config.sessionLimit),
  noSessionLimit: Number(config.noSessionLimit),
  ipLimit: Number(config.ipLimit),
  sessionPageLimit: Number(config.sessionPageLimit),
  noSessionPageLimit: Number(config.noSessionPageLimit),
})

/**
 * Limits the proxy routes and the pages that call the API during SSR.
 * Page loads without a session share one budget per Nuxt task, so that a
 * crawler spread over many IP addresses can't make SSR call the API without
 * a bound. Past it, they get a 503 before SSR starts.
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
  limiter ??= createLimiter(config.windowSeconds * 1000, enforce)

  const sessionConfig = getSessionConfig(
    runtimeConfig.hmacSigningSecret,
    runtimeConfig.public.deploymentEnv
  )
  const session = sessionConfig
    ? await getRequestSession(event, sessionConfig)
    : { id: null, state: "none" as const }

  const ip = getIpRateLimitKey(getClientIp(event))
  const result = limiter.hit(
    getRateLimitChecks({ kind, sessionId: session.id, ip, config })
  )
  const isRejected = Boolean(result) && enforce
  // A rejected request doesn't start a session, so that a flood of requests
  // without a session costs nothing more than counting them.
  if (sessionConfig && !isRejected) {
    await renewSession(event, sessionConfig)
  }
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
  // The shared budget limits the server, not the client, so it answers like
  // an overloaded server. It rejects the request before SSR calls the API.
  const overloaded = result.counter === "no-session-page"
  throw createError({
    statusCode: overloaded ? 503 : 429,
    statusMessage: overloaded ? "Service Unavailable" : "Too Many Requests",
    data: { retryAfter: result.retryAfterSeconds },
  })
})
