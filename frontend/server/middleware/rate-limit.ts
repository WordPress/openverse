import { useRuntimeConfig } from "nitropack/runtime"
import {
  createError,
  defineEventHandler,
  getCookie,
  getRequestURL,
  setResponseHeader,
  unsealSession,
  type H3Event,
  type SessionConfig,
} from "h3"
import { logger } from "~~/server/utils/logger"
import { isInternalRequest } from "~~/server/utils/proxy"
import {
  getClientIp,
  getRateLimitChecks,
  getRateLimitedRequestKind,
  RateLimiter,
  type RateLimitConfig,
} from "~~/server/utils/rate-limit"

import { getSessionConfig } from "#shared/utils/session"

let limiter: RateLimiter | null = null
let nextSummaryAt = 0

const readSessionId = async (event: H3Event, config: SessionConfig | null) => {
  if (!config?.name) {
    return null
  }
  const sealed = getCookie(event, config.name)
  if (!sealed) {
    return null
  }
  try {
    const session = await unsealSession(event, config, sealed)
    return typeof session.id === "string" && session.id ? session.id : null
  } catch {
    // An expired or forged session is the same as no session.
    return null
  }
}

const toRateLimitConfig = (
  config: Record<string, unknown>
): RateLimitConfig => ({
  mode: String(config.mode),
  windowSeconds: Number(config.windowSeconds),
  sessionLimit: Number(config.sessionLimit),
  noSessionLimit: Number(config.noSessionLimit),
  ipLimit: Number(config.ipLimit),
  trustedProxies: Number(config.trustedProxies),
})

/**
 * Limits the proxy routes and the pages that call the API during SSR.
 * In `log` mode, it only logs the requests that would be limited. Session
 * values and IP addresses are never logged.
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
  limiter ??= new RateLimiter(config.windowSeconds * 1000)

  const sessionId = await readSessionId(
    event,
    getSessionConfig(
      runtimeConfig.hmacSigningSecret,
      runtimeConfig.public.deploymentEnv
    )
  )
  const ip = getClientIp(event, config.trustedProxies)
  const result = limiter.hit(
    getRateLimitChecks({ kind, sessionId, ip, config })
  )

  const now = Date.now()
  if (now >= nextSummaryAt) {
    nextSummaryAt = now + config.windowSeconds * 1000
    const counts = limiter.takeLimitedCounts()
    if (Object.values(counts).some(Boolean)) {
      logger.info("Rate limited requests by counter", counts)
    }
  }

  if (!result) {
    return
  }

  const enforce = config.mode === "enforce"
  if (result.isFirstExceeded) {
    logger.warn("Rate limit exceeded", {
      counter: result.counter,
      requestKind: kind,
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
