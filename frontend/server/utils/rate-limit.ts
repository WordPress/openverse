import { createHmac, randomBytes } from "node:crypto"
import { isIPv6 } from "node:net"

import { getRequestHeader, getRequestIP, type H3Event } from "h3"

export type RateLimitCounter =
  | "session"
  | "session-page"
  | "no-session"
  | "no-session-page"
  | "ip"
export type RateLimitedRequestKind = "api" | "page"

export interface RateLimitConfig {
  mode: string
  windowSeconds: number
  sessionLimit: number
  noSessionLimit: number
  ipLimit: number
  /** Server-rendered page loads per session. */
  sessionPageLimit: number
  /**
   * Page loads without a session that one Nuxt task renders in a window,
   * from all clients together.
   */
  noSessionPageLimit: number
}

export interface RateLimitCheck {
  counter: RateLimitCounter
  key: string
  limit: number
  /**
   * The session that made the request, for the per-IP ceiling. The window
   * counts how many sessions it saw, to tell a shared address apart from a
   * single client.
   */
  sessionId?: string | null
}

export interface RateLimitResult {
  counter: RateLimitCounter
  /**
   * A short hash of the session ID or IP address, which is the same for all
   * the log lines of one key in this process.
   */
  keyHash: string
  limit: number
  retryAfterSeconds: number
  /** Whether this is the first request over the limit in the window. */
  isFirstExceeded: boolean
}

/** A window that went over its limit, reported when it ends. */
export interface ExceededWindow {
  counter: RateLimitCounter
  keyHash: string
  limit: number
  windowSeconds: number
  /** When the window ended, because it is reported later than that. */
  windowEnd: string
  requests: number
  /**
   * The requests that this counter limited. A request over several limits is
   * counted only by the first one, so the sum over the windows is the number
   * of limited requests.
   */
  limitedRequests: number
  /** Only for the per-IP ceiling. */
  sessions?: number
  /** Only for the per-IP ceiling: requests that had no valid session. */
  noSessionRequests?: number
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

/**
 * The most sessions a window keeps track of, so that a client that sends many
 * session cookies can't use up the memory.
 */
const MAX_TRACKED_SESSIONS = 10_000

interface Window {
  counter: RateLimitCounter
  keyHash: string
  limit: number
  count: number
  limited: number
  resetAt: number
  sessions?: Set<string>
  noSessionRequests?: number
}

/**
 * In-memory fixed-window counters. They are per Nuxt task, so the limits are
 * approximate. Session IDs and IP addresses are never stored: the counters
 * are keyed by their HMAC with a random key that is generated for each
 * limiter and never leaves the process. Expired counters are removed at the
 * first request after the end of the next window.
 *
 * Each window that went over its limit is passed to `onExceededWindow` after
 * it ends: when the key's next window starts, or when it's removed by `prune`
 * or `flush`.
 */
export class RateLimiter {
  private windows = new Map<string, Window>()
  private nextPruneAt = 0

  private hashKey = randomBytes(32)

  constructor(
    private windowMs: number,
    private now: () => number = Date.now,
    private onExceededWindow: (window: ExceededWindow) => void = () => {}
  ) {}

  private hash(value: string) {
    return createHmac("sha256", this.hashKey).update(value).digest("base64url")
  }

  /**
   * Counts the request in every check and returns the first exceeded limit,
   * or `null` if the request is under all the limits.
   */
  hit(checks: RateLimitCheck[]): RateLimitResult | null {
    const now = this.now()
    if (now >= this.nextPruneAt) {
      this.prune()
    }

    let result: RateLimitResult | null = null
    for (const { counter, key, limit, sessionId } of checks) {
      const keyHash = this.hash(key)
      const windowKey = `${counter}:${keyHash}`
      let window = this.windows.get(windowKey)
      if (!window || window.resetAt <= now) {
        if (window) {
          this.report(window)
        }
        window = {
          counter,
          keyHash: keyHash.slice(0, 12),
          limit,
          count: 0,
          limited: 0,
          resetAt: now + this.windowMs,
        }
        this.windows.set(windowKey, window)
      }
      window.count += 1
      if (sessionId !== undefined) {
        if (!sessionId) {
          window.noSessionRequests = (window.noSessionRequests ?? 0) + 1
        } else {
          window.sessions ??= new Set()
          if (window.sessions.size < MAX_TRACKED_SESSIONS) {
            window.sessions.add(this.hash(sessionId))
          }
        }
      }
      if (!result && window.count > limit) {
        window.limited += 1
        result = {
          counter,
          keyHash: window.keyHash,
          limit,
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

  get size() {
    return this.windows.size
  }

  private report(window: Window) {
    if (window.count <= window.limit) {
      return
    }
    const trackedSessions = window.counter === "ip"
    this.onExceededWindow({
      counter: window.counter,
      keyHash: window.keyHash,
      limit: window.limit,
      windowSeconds: this.windowMs / 1000,
      windowEnd: new Date(window.resetAt).toISOString(),
      requests: window.count,
      limitedRequests: window.limited,
      ...(trackedSessions && {
        sessions: window.sessions?.size ?? 0,
        noSessionRequests: window.noSessionRequests ?? 0,
      }),
    })
  }

  /**
   * Removes the windows that ended. `hit` does this at most once per window;
   * calling it on a timer reports the exceeded windows of a task that gets no
   * more requests.
   */
  prune() {
    const now = this.now()
    for (const [key, window] of this.windows) {
      if (window.resetAt <= now) {
        this.report(window)
        this.windows.delete(key)
      }
    }
    this.nextPruneAt = now + this.windowMs
  }

  /**
   * Removes all the windows, including the ones that have not ended, so that
   * the exceeded ones are reported before the process stops.
   */
  flush() {
    for (const window of this.windows.values()) {
      this.report(window)
    }
    this.windows.clear()
  }
}

/**
 * The key of the counter that all the page loads without a session share.
 */
const NO_SESSION_PAGE_KEY = "all"

/**
 * Returns the counters that a request is counted by.
 * - A request with a session counts toward its session limit.
 * - A page load with a session also counts toward its low page limit, because
 *   after the first page, people navigate without loading pages from the
 *   server.
 * - An `/api` request without a session counts toward the low per-IP limit.
 * - A page load without a session counts toward a budget that all such page
 *   loads share, because every new visitor arrives this way, and a crawler
 *   that spreads its requests over many IP addresses stays under any per-IP
 *   limit.
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
    if (kind === "page") {
      checks.push({
        counter: "session-page",
        key: sessionId,
        limit: config.sessionPageLimit,
      })
    }
  } else if (kind === "api") {
    checks.push({
      counter: "no-session",
      key: ip,
      limit: config.noSessionLimit,
    })
  } else {
    checks.push({
      counter: "no-session-page",
      key: NO_SESSION_PAGE_KEY,
      limit: config.noSessionPageLimit,
    })
  }
  checks.push({ counter: "ip", key: ip, limit: config.ipLimit, sessionId })
  return checks
}
