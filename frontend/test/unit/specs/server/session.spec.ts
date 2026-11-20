import { IncomingMessage, ServerResponse } from "node:http"
import { Socket } from "node:net"

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
import { createEvent, sealSession, type H3Event, type SessionConfig } from "h3"

import {
  ensureSession,
  getSessionConfig,
  SESSION_MAX_AGE_SECONDS,
  SESSION_NAME,
  SESSION_RENEW_AFTER_SECONDS,
} from "#shared/utils/session"

const config = getSessionConfig(
  "a-test-secret-that-is-at-least-32-characters-long",
  "production"
) as SessionConfig

const makeEvent = (cookie?: string) => {
  const req = new IncomingMessage(new Socket())
  if (cookie) {
    req.headers.cookie = cookie
  }
  return createEvent(req, new ServerResponse(req))
}

const getSetCookies = (event: H3Event) =>
  [event.node.res.getHeader("set-cookie") ?? []].flat().map(String)

/** Returns a cookie header with a session sealed `ageSeconds` ago. */
const sessionCookie = async (ageSeconds: number, id = "existing") => {
  const event = makeEvent()
  event.context.sessions = {
    [SESSION_NAME]: {
      id,
      createdAt: Date.now() - ageSeconds * 1000,
      data: {},
    },
  }
  return `${SESSION_NAME}=${await sealSession(event, config)}`
}

describe("ensureSession", () => {
  beforeEach(() => {
    vi.useFakeTimers({ now: new Date("2026-11-19T12:00:00Z") })
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it("starts a session when the request has none", async () => {
    const event = makeEvent()
    expect(await ensureSession(event, config)).toEqual({
      id: null,
      state: "none",
    })
    const [cookie] = getSetCookies(event)
    expect(cookie).toMatch(new RegExp(`^${SESSION_NAME}=`))
    expect(cookie).toContain("HttpOnly")
    expect(cookie).toContain("Secure")
  })

  it("keeps a session younger than the renewal age", async () => {
    const event = makeEvent(await sessionCookie(60))
    expect(await ensureSession(event, config)).toEqual({
      id: "existing",
      state: "valid",
    })
    expect(getSetCookies(event)).toEqual([])
  })

  it("counts an old session and replaces it with a new one", async () => {
    const event = makeEvent(
      await sessionCookie(SESSION_RENEW_AFTER_SECONDS + 1)
    )
    expect(await ensureSession(event, config)).toEqual({
      id: "existing",
      state: "valid",
    })
    expect(getSetCookies(event)).toHaveLength(1)
    expect(event.context.sessions?.[SESSION_NAME].id).not.toEqual("existing")
  })

  it.each`
    name         | cookie
    ${"expired"} | ${() => sessionCookie(SESSION_MAX_AGE_SECONDS + 1)}
    ${"forged"}  | ${() => Promise.resolve(`${SESSION_NAME}=forged`)}
  `(
    "treats an $name session as invalid and starts a new one",
    async ({ cookie }) => {
      const event = makeEvent(await cookie())
      expect(await ensureSession(event, config)).toEqual({
        id: null,
        state: "invalid",
      })
      expect(getSetCookies(event)).toHaveLength(1)
    }
  )

  it("sets the cookie only once for a request", async () => {
    const event = makeEvent()
    await ensureSession(event, config)
    await ensureSession(event, config)
    expect(getSetCookies(event)).toHaveLength(1)
  })
})
