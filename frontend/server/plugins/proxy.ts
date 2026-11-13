import { randomUUID } from "node:crypto"

import { defineNitroPlugin, useRuntimeConfig } from "nitropack/runtime"
import { createOpenverseApiClient } from "~~/server/utils/api-client"
import { logger } from "~~/server/utils/logger"

import { LOCAL } from "#shared/constants/deploy-env"
import { getSessionConfig } from "#shared/utils/session"

/**
 * Creates the Openverse API client for the proxy routes and adds it to the
 * event context as `event.context.apiClient`.
 *
 * Outside the local environment, the proxied requests must be authenticated.
 * Without the API credentials, the client is not created and the proxy routes
 * return 500, but the rest of the site keeps working, for example, when the
 * `proxy_requests` flag is off or in the Playwright tests.
 */
export default defineNitroPlugin((nitroApp) => {
  const config = useRuntimeConfig()
  const isLocal = config.public.deploymentEnv === LOCAL
  const { apiClientId: clientId, apiClientSecret: clientSecret } = config

  const hasCredentials = Boolean(clientId && clientSecret)
  if (!hasCredentials) {
    if (isLocal) {
      logger.warn(
        "API client ID and secret are not set. Proxied API requests are anonymous."
      )
    } else {
      logger.error(
        "API client ID and secret are not set. The proxy routes are disabled."
      )
    }
  }

  if (
    !getSessionConfig(config.hmacSigningSecret, config.public.deploymentEnv)
  ) {
    logger.error(
      "The session secret is missing or shorter than 32 characters. Rate limits count all requests by IP address."
    )
  }

  const apiUrl = config.apiUrlInternal || config.public.apiUrl
  const apiClient =
    hasCredentials || isLocal
      ? createOpenverseApiClient({
          apiUrl,
          credentials: hasCredentials ? { clientId, clientSecret } : undefined,
        })
      : undefined
  // Only this process knows the token, so a client can't send it to skip the
  // rate limits. See `isInternalRequest`.
  const internalRequestToken = randomUUID()

  if (apiClient) {
    logger.info(`Initialized the Openverse API client with base URL ${apiUrl}`)
  }

  nitroApp.hooks.hook("request", (event) => {
    event.context.apiClient = apiClient
    event.context.internalRequestToken = internalRequestToken
  })
})
