import { LOCAL, type DeployEnv } from "#shared/constants/deploy-env"

import type { SessionConfig } from "h3"

export const SESSION_NAME = "ovSession"
export const SESSION_MAX_AGE_SECONDS = 60 * 60 * 24

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
