import { createHmac, randomBytes } from "node:crypto"
import { isIPv6 } from "node:net"

import { getRequestHeader, getRequestIP, type H3Event } from "h3"

export type RateLimitCounter = "session" | "no-session" | "ip"
export type RateLimitedRequestKind = "api" | "page"

export interface RateLimitConfig {
  mode: string
  windowSeconds: number
  sessionLimit: number
  noSessionLimit: number
  ipLimit: number
}

export interface RateLimitCheck {
  counter: RateLimitCounter
  key: string
  limit: number
}

export interface RateLimitResult {
  counter: RateLimitCounter
  retryAfterSeconds: number
  /** Whether this is the first request over the limit in the window. */
  isFirstExceeded: boolean
}

const PROXY_ROUTE_PATTERN =
  /^\/api\/(?:search\/[^/]+|[^/]+\/related\/[^/]+|[^/]+\/[^/]+)\/?$/
/**
 * The pages that call the API during SSR, with an optional locale prefix:
 * search, collection and single result pages.
 */
const API_PAGE_PATTERN =
  /^(?:\/[a-z]{2,3}(?:-[a-z0-9]+)*)?\/(?:search(?:\/(?:image|audio))?|(?:image|audio)\/[^/]+(?:\/.*)?)\/?$/

/**
 * Returns which kind of rate-limited request this is, or `null` if the
 * request is not rate-limited.
 */
export const getRateLimitedRequestKind = (
  pathname: string
): RateLimitedRequestKind | null => {
  if (PROXY_ROUTE_PATTERN.test(pathname)) {
    return "api"
  }
  if (API_PAGE_PATTERN.test(pathname)) {
    return "page"
  }
  return null
}

/**
 * Returns the client IP address that Cloudflare sets in `CF-Connecting-IP`.
 * The load balancer only accepts requests from Cloudflare, so clients cannot
 * set this header themselves. Without Cloudflare, for example locally, it
 * falls back to the socket address.
 */
export const getClientIp = (event: H3Event) =>
  getRequestHeader(event, "cf-connecting-ip")?.trim() ||
  getRequestIP(event) ||
  "unknown"

const expandIpv6 = (address: string) => {
  const toGroups = (part: string) =>
    part
      ? part.split(":").flatMap((group) => {
          if (!group.includes(".")) {
            return [parseInt(group, 16)]
          }
          const [a, b, c, d] = group.split(".").map(Number)
          return [(a << 8) | b, (c << 8) | d]
        })
      : []
  const [head, tail] = address.split("::")
  const headGroups = toGroups(head)
  if (tail === undefined) {
    return headGroups
  }
  const tailGroups = toGroups(tail)
  const zeros = Array(8 - headGroups.length - tailGroups.length).fill(0)
  return [...headGroups, ...zeros, ...tailGroups]
}

/**
 * Returns the address that the per-IP limits count by. An IPv6 client usually
 * gets a whole /64 network, so it is counted by its /64 prefix and cannot get
 * around the limits by changing addresses inside it.
 */
export const getIpRateLimitKey = (ip: string) => {
  const address = ip.split("%")[0]
  if (!isIPv6(address)) {
    return ip
  }
  const groups = expandIpv6(address)
  if (
    groups.slice(0, 6).every((group, i) => group === (i === 5 ? 0xffff : 0))
  ) {
    return `${groups[6] >> 8}.${groups[6] & 0xff}.${groups[7] >> 8}.${groups[7] & 0xff}`
  }
  return `${groups
    .slice(0, 4)
    .map((group) => group.toString(16))
    .join(":")}::/64`
}

interface Window {
  count: number
  resetAt: number
}

/**
 * In-memory fixed-window counters. They are per Nuxt task, so the limits are
 * approximate. Session IDs and IP addresses are never stored: the counters
 * are keyed by their HMAC with a random key that is generated for each
 * limiter and never leaves the process. Expired counters are removed at the
 * first request after the end of the next window.
 */
export class RateLimiter {
  private windows = new Map<string, Window>()
  private limited: Record<RateLimitCounter, number> = {
    session: 0,
    "no-session": 0,
    ip: 0,
  }
  private nextPruneAt = 0

  private hashKey = randomBytes(32)

  constructor(
    private windowMs: number,
    private now: () => number = Date.now
  ) {}

  /**
   * Counts the request in every check and returns the first exceeded limit,
   * or `null` if the request is under all the limits.
   */
  hit(checks: RateLimitCheck[]): RateLimitResult | null {
    const now = this.now()
    this.prune(now)

    let result: RateLimitResult | null = null
    for (const { counter, key, limit } of checks) {
      const windowKey = createHmac("sha256", this.hashKey)
        .update(`${counter}:${key}`)
        .digest("base64url")
      let window = this.windows.get(windowKey)
      if (!window || window.resetAt <= now) {
        window = { count: 0, resetAt: now + this.windowMs }
        this.windows.set(windowKey, window)
      }
      window.count += 1
      if (!result && window.count > limit) {
        this.limited[counter] += 1
        result = {
          counter,
          retryAfterSeconds: Math.max(
            Math.ceil((window.resetAt - now) / 1000),
            1
          ),
          isFirstExceeded: window.count === limit + 1,
        }
      }
    }
    return result
  }

  /**
   * Returns the number of limited requests by counter since the last call,
   * and resets them.
   */
  takeLimitedCounts() {
    const counts = { ...this.limited }
    this.limited = { session: 0, "no-session": 0, ip: 0 }
    return counts
  }

  get size() {
    return this.windows.size
  }

  private prune(now: number) {
    if (now < this.nextPruneAt) {
      return
    }
    for (const [key, window] of this.windows) {
      if (window.resetAt <= now) {
        this.windows.delete(key)
      }
    }
    this.nextPruneAt = now + this.windowMs
  }
}

/**
 * Returns the counters that a request is counted by.
 * - A request with a session counts toward its session limit.
 * - An `/api` request without a session counts toward the low per-IP limit.
 * - A page load without a session counts only toward the per-IP ceiling,
 *   because every new visitor arrives this way.
 * - Every request counts toward the per-IP ceiling.
 */
export const getRateLimitChecks = ({
  kind,
  sessionId,
  ip,
  config,
}: {
  kind: RateLimitedRequestKind
  sessionId: string | null
  ip: string
  config: RateLimitConfig
}): RateLimitCheck[] => {
  const checks: RateLimitCheck[] = []
  if (sessionId) {
    checks.push({
      counter: "session",
      key: sessionId,
      limit: config.sessionLimit,
    })
  } else if (kind === "api") {
    checks.push({
      counter: "no-session",
      key: ip,
      limit: config.noSessionLimit,
    })
  }
  checks.push({ counter: "ip", key: ip, limit: config.ipLimit })
  return checks
}
