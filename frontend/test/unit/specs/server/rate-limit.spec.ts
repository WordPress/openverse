import { describe, expect, it } from "vitest"
import {
  getClientIp,
  getRateLimitChecks,
  getRateLimitedRequestKind,
  RateLimiter,
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

  it("reports the limited requests by counter", () => {
    const limiter = new RateLimiter(60_000, () => 0)
    for (let i = 0; i < config.sessionLimit + 2; i++) {
      limiter.hit(checks)
    }
    expect(limiter.takeLimitedCounts()).toEqual({
      session: 2,
      "no-session": 0,
      ip: 0,
    })
    expect(limiter.takeLimitedCounts().session).toEqual(0)
  })
})
