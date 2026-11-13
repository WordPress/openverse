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
 * Outside the local environment, the proxied requests must be authenticated,
 * so the server does not start without the API credentials.
 */
export default defineNitroPlugin((nitroApp) => {
  const config = useRuntimeConfig()
  const isLocal = config.public.deploymentEnv === LOCAL
  const { apiClientId: clientId, apiClientSecret: clientSecret } = config

  if (!clientId || !clientSecret) {
    if (!isLocal) {
      throw new Error(
        "API client ID and secret are not set, cannot create the Openverse API client."
      )
    }
    logger.warn(
      "API client ID and secret are not set. Proxied API requests are anonymous."
    )
  }

  if (
    !getSessionConfig(config.hmacSigningSecret, config.public.deploymentEnv)
  ) {
    logger.error(
      "The session secret is missing or shorter than 32 characters. Rate limits count all requests by IP address."
    )
  }

  const apiUrl = config.apiUrlInternal || config.public.apiUrl
  const apiClient = createOpenverseApiClient({
    apiUrl,
    credentials:
      clientId && clientSecret ? { clientId, clientSecret } : undefined,
  })
  // Only this process knows the token, so a client can't send it to skip the
  // rate limits. See `isInternalRequest`.
  const internalRequestToken = randomUUID()

  logger.info(`Initialized the Openverse API client with base URL ${apiUrl}`)

  nitroApp.hooks.hook("request", (event) => {
    event.context.apiClient = apiClient
    event.context.internalRequestToken = internalRequestToken
  })
})
