import { describe, expect, it } from "vitest"
import {
  getClientIp,
  getIpRateLimitKey,
  getRateLimitChecks,
  getRateLimitedRequestKind,
  RateLimiter,
  type ExceededWindow,
  type RateLimitConfig,
} from "~~/server/utils/rate-limit"

import type { H3Event } from "h3"

const config: RateLimitConfig = {
  mode: "log",
  windowSeconds: 60,
  sessionLimit: 3,
  noSessionLimit: 1,
  ipLimit: 5,
}

const eventWithHeaders = (headers: Record<string, string>) =>
  ({
    node: { req: { headers, socket: { remoteAddress: "10.0.0.1" } } },
    headers: new Headers(headers),
    context: {},
  }) as unknown as H3Event

describe("getRateLimitedRequestKind", () => {
  it.each([
    ["/api/search/image/", "api"],
    ["/api/search/audio", "api"],
    ["/api/image/2a2a1c2e-6a3b-4d5c-9e8f-0a1b2c3d4e5f/", "api"],
    ["/api/audio/related/2a2a1c2e-6a3b-4d5c-9e8f-0a1b2c3d4e5f/", "api"],
    ["/search", "page"],
    ["/search/image/", "page"],
    ["/ru/search/audio", "page"],
    ["/pt-br/image/2a2a1c2e-6a3b-4d5c-9e8f-0a1b2c3d4e5f", "page"],
    ["/image/source/flickr/", "page"],
    ["/api/sources", null],
    ["/", null],
    ["/about", null],
    ["/_nuxt/entry.js", null],
    ["/search/model-3d", null],
  ])("returns the kind for %s", (path, expected) => {
    expect(getRateLimitedRequestKind(path)).toEqual(expected)
  })
})

describe("getClientIp", () => {
  it("uses the address that Cloudflare sets", () => {
    const event = eventWithHeaders({
      "cf-connecting-ip": "1.1.1.1",
      "x-forwarded-for": "2.2.2.2, 1.1.1.1, 3.3.3.3",
    })
    expect(getClientIp(event)).toEqual("1.1.1.1")
  })

  it("ignores X-Forwarded-For without the Cloudflare header", () => {
    const event = eventWithHeaders({ "x-forwarded-for": "2.2.2.2" })
    expect(getClientIp(event)).toEqual("10.0.0.1")
  })
})

describe("getIpRateLimitKey", () => {
  it.each`
    ip                                    | expected
    ${"203.0.113.7"}                      | ${"203.0.113.7"}
    ${"2001:db8:85a3:12:8a2e:370:7334:1"} | ${"2001:db8:85a3:12::/64"}
    ${"2001:DB8:85A3:0012::1"}            | ${"2001:db8:85a3:12::/64"}
    ${"2001:db8::1"}                      | ${"2001:db8:0:0::/64"}
    ${"1::2:3:4:5:6:7"}                   | ${"1:0:2:3::/64"}
    ${"fe80::1%eth0"}                     | ${"fe80:0:0:0::/64"}
    ${"::ffff:203.0.113.7"}               | ${"203.0.113.7"}
    ${"64:ff9b::203.0.113.7"}             | ${"64:ff9b:0:0::/64"}
    ${"unknown"}                          | ${"unknown"}
  `("counts $ip as $expected", ({ ip, expected }) => {
    expect(getIpRateLimitKey(ip)).toEqual(expected)
  })
})

describe("getRateLimitChecks", () => {
  it.each`
    kind      | sessionId | expected
    ${"api"}  | ${"s1"}   | ${["session", "ip"]}
    ${"api"}  | ${null}   | ${["no-session", "ip"]}
    ${"page"} | ${"s1"}   | ${["session", "ip"]}
    ${"page"} | ${null}   | ${["ip"]}
  `(
    "counts $kind requests with session $sessionId by $expected",
    ({ kind, sessionId, expected }) => {
      const checks = getRateLimitChecks({
        kind,
        sessionId,
        ip: "1.1.1.1",
        config,
      })
      expect(checks.map(({ counter }) => counter)).toEqual(expected)
    }
  )
})

describe("RateLimiter", () => {
  const checks = getRateLimitChecks({
    kind: "api",
    sessionId: "s1",
    ip: "1.1.1.1",
    config,
  })

  it("returns the exceeded counter after the limit", () => {
    const limiter = new RateLimiter(60_000, () => 0)
    for (let i = 0; i < config.sessionLimit; i++) {
      expect(limiter.hit(checks)).toBeNull()
    }
    expect(limiter.hit(checks)).toEqual({
      counter: "session",
      keyHash: expect.any(String),
      limit: config.sessionLimit,
      retryAfterSeconds: 60,
      isFirstExceeded: true,
    })
    expect(limiter.hit(checks)?.isFirstExceeded).toBe(false)
  })

  it("counts sessions on one IP separately, up to the IP ceiling", () => {
    const limiter = new RateLimiter(60_000, () => 0)
    const hitAs = (sessionId: string) =>
      limiter.hit(
        getRateLimitChecks({ kind: "api", sessionId, ip: "1.1.1.1", config })
      )
    for (let i = 0; i < config.ipLimit; i++) {
      expect(hitAs(`session-${i}`)).toBeNull()
    }
    expect(hitAs("another-session")?.counter).toEqual("ip")
  })

  it("resets the counters after the window", () => {
    let now = 0
    const limiter = new RateLimiter(60_000, () => now)
    for (let i = 0; i <= config.sessionLimit; i++) {
      limiter.hit(checks)
    }
    now = 60_000
    expect(limiter.hit(checks)).toBeNull()
    expect(limiter.size).toEqual(2)
  })

  it("does not store session IDs or IP addresses", () => {
    const limiter = new RateLimiter(60_000, () => 0)
    limiter.hit(checks)
    const stored = JSON.stringify(
      [...(limiter as unknown as { windows: Map<string, unknown> }).windows],
      (_, value) => (value instanceof Set ? [...value] : value)
    )
    expect(stored).not.toContain("s1")
    expect(stored).not.toContain("1.1.1.1")
  })

  it("reports each exceeded window once, when it ends", () => {
    let now = 0
    const reported: ExceededWindow[] = []
    const limiter = new RateLimiter(
      60_000,
      () => now,
      (window) => reported.push(window)
    )
    for (let i = 0; i < config.sessionLimit + 2; i++) {
      limiter.hit(checks)
    }
    expect(reported).toEqual([])

    now = 60_000
    limiter.hit(checks)
    expect(reported).toEqual([
      {
        counter: "session",
        keyHash: expect.any(String),
        limit: config.sessionLimit,
        windowSeconds: 60,
        requests: config.sessionLimit + 2,
        limitedRequests: 2,
      },
    ])
  })

  it("does not report windows under the limit", () => {
    let now = 0
    const reported: ExceededWindow[] = []
    const limiter = new RateLimiter(
      60_000,
      () => now,
      (window) => reported.push(window)
    )
    limiter.hit(checks)
    now = 120_000
    limiter.hit(checks)
    expect(reported).toEqual([])
  })

  it("reports how many sessions shared an exceeded IP window", () => {
    let now = 0
    const reported: ExceededWindow[] = []
    const limiter = new RateLimiter(
      60_000,
      () => now,
      (window) => reported.push(window)
    )
    const hitAs = (sessionId: string | null) =>
      limiter.hit(
        getRateLimitChecks({ kind: "page", sessionId, ip: "1.1.1.1", config })
      )
    for (const sessionId of ["a", "a", "b", "c", null, null]) {
      hitAs(sessionId)
    }
    now = 60_000
    hitAs("a")
    expect(reported).toEqual([
      expect.objectContaining({
        counter: "ip",
        requests: 6,
        limitedRequests: 1,
        sessions: 3,
        noSessionRequests: 2,
      }),
    ])
  })

  it("uses the same key hash for the counters of one IP address", () => {
    const limiter = new RateLimiter(60_000, () => 0)
    const noSessionChecks = getRateLimitChecks({
      kind: "api",
      sessionId: null,
      ip: "1.1.1.1",
      config: { ...config, ipLimit: 0 },
    })
    const ipResult = limiter.hit(noSessionChecks)
    expect(ipResult?.counter).toEqual("ip")
    const noSessionResult = limiter.hit(noSessionChecks)
    expect(noSessionResult?.counter).toEqual("no-session")
    expect(noSessionResult?.keyHash).toEqual(ipResult?.keyHash)
    expect(ipResult?.keyHash).not.toContain("1.1.1.1")
  })
})
