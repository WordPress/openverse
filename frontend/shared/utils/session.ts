import {
  getCookie,
  unsealSession,
  updateSession,
  type H3Event,
  type SessionConfig,
} from "h3"

import { LOCAL, type DeployEnv } from "#shared/constants/deploy-env"

export const SESSION_NAME = "ovSession"
export const SESSION_MAX_AGE_SECONDS = 60 * 60 * 24
/**
 * A session older than this is replaced with a new one, so that people who
 * keep using a tab for longer than the session lifetime keep a session.
 */
export const SESSION_RENEW_AFTER_SECONDS = SESSION_MAX_AGE_SECONDS / 2

/**
 * Used only in the local environment, so that the session works without
 * setting up a secret. h3 requires the password to be at least 32 characters.
 */
const LOCAL_SESSION_SECRET = "openverse-local-development-session-secret"

/**
 * Returns the config for the anonymous session that the Nitro rate limits use
 * to tell apart the people who share an IP address, or `null` if the session
 * secret is not set outside the local environment.
 *
 * The session is read only from the cookie, so `sessionHeader` is disabled.
 */
export const getSessionConfig = (
  secret: string,
  deploymentEnv: DeployEnv | string
): SessionConfig | null => {
  const isLocal = deploymentEnv === LOCAL
  const password = secret || (isLocal ? LOCAL_SESSION_SECRET : "")
  if (password.length < 32) {
    return null
  }
  return {
    name: SESSION_NAME,
    password,
    maxAge: SESSION_MAX_AGE_SECONDS,
    sessionHeader: false,
    cookie: {
      httpOnly: true,
      secure: !isLocal,
      sameSite: "lax",
      path: "/",
    },
  }
}

/**
 * `none`: the request has no session cookie.
 * `invalid`: the cookie is expired, forged or sealed with another secret.
 */
export type RequestSessionState = "none" | "invalid" | "valid"

export interface RequestSession {
  /** The ID of the valid session that the request came with. */
  id: string | null
  state: RequestSessionState
}

interface ReadSession extends RequestSession {
  createdAt?: number
}

const requestSessions = new WeakMap<H3Event, Promise<ReadSession>>()
const sessionRenewals = new WeakMap<H3Event, Promise<void>>()

const unsealRequestSession = async (
  event: H3Event,
  config: SessionConfig
): Promise<ReadSession> => {
  const sealed = getCookie(event, SESSION_NAME)
  if (!sealed) {
    return { id: null, state: "none" }
  }
  try {
    // Checks the seal and that the session is younger than `maxAge`.
    const { id, createdAt } = await unsealSession(event, config, sealed)
    if (typeof id === "string" && id && typeof createdAt === "number") {
      return { id, state: "valid", createdAt }
    }
  } catch {
    // An expired or forged session is the same as no session.
  }
  return { id: null, state: "invalid" }
}

const readSession = (event: H3Event, config: SessionConfig) => {
  let session = requestSessions.get(event)
  if (!session) {
    session = unsealRequestSession(event, config)
    requestSessions.set(event, session)
  }
  return session
}

/**
 * Returns the session that the request came with, without changing it. The
 * result is cached for each request.
 */
export const getRequestSession = async (
  event: H3Event,
  config: SessionConfig
): Promise<RequestSession> => {
  const { id, state } = await readSession(event, config)
  return { id, state }
}

/**
 * Returns the ID of the session that replaces `id`. Requests that a tab sends
 * together with one old session each renew it, and the browser keeps only one
 * of their cookies. Deriving the ID gives them all the same new session.
 */
const getRenewedSessionId = async (id: string) => {
  const digest = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(id)
  )
  return Array.from(new Uint8Array(digest), (byte) =>
    byte.toString(16).padStart(2, "0")
  ).join("")
}

/**
 * Sets a new session cookie on the response. h3 checks a session's age from
 * its creation time, which `updateSession` keeps, so renewing a session means
 * starting a new one with a new ID.
 */
const startSession = async (
  event: H3Event,
  config: SessionConfig,
  id: string
) => {
  event.context.sessions ??= Object.create(null)
  event.context.sessions![SESSION_NAME] = {
    id,
    createdAt: Date.now(),
    data: {},
  }
  await updateSession(event, config)
}

/**
 * Starts a new session in the response if the request has no valid session,
 * or if its session is older than `SESSION_RENEW_AFTER_SECONDS`. It sets the
 * cookie at most once for each request.
 */
export const renewSession = (event: H3Event, config: SessionConfig) => {
  let renewal = sessionRenewals.get(event)
  if (!renewal) {
    renewal = (async () => {
      const { id, createdAt } = await readSession(event, config)
      if (!id) {
        await startSession(event, config, crypto.randomUUID())
      } else if (
        Date.now() >=
        (createdAt ?? 0) + SESSION_RENEW_AFTER_SECONDS * 1000
      ) {
        await startSession(event, config, await getRenewedSessionId(id))
      }
    })()
    sessionRenewals.set(event, renewal)
  }
  return renewal
}

/**
 * Returns the session that the request came with, and renews it.
 *
 * The rate limits count the request by the session it came with, so dropping
 * the cookie to get a new session doesn't help a client avoid them. A client
 * can already get a new session by loading a page; the per-IP ceiling limits
 * all of them together.
 */
export const ensureSession = async (event: H3Event, config: SessionConfig) => {
  const session = await getRequestSession(event, config)
  await renewSession(event, config)
  return session
}
