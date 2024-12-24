import { getRequestURL } from "h3"
import { defineNitroPlugin } from "nitropack/runtime"
import { createClient } from "@openverse/api-client"
import { logger } from "~~/server/utils/logger"
import { sendServerPlausibleEvent } from "~~/server/utils/plausible"

import { buildEventPayload } from "#shared/utils/search-response-time-payload"

logger.withTag("openverse:proxy")

const sendEvent = (response: Response, request: Request, requestTime: Date) => {
  const responseHeaders = Object.fromEntries(response.headers.entries())
  const requestQuery = new URL(request.url).search
  const searchTimeEventPayload = buildEventPayload(
    responseHeaders,
    requestQuery,
    requestTime,
    "image"
  )

  logger.verbose({ searchTimeEventPayload })
  if (searchTimeEventPayload) {
    sendServerPlausibleEvent("SEARCH_RESPONSE_TIME", searchTimeEventPayload, {
      r: responseHeaders.referer ?? "",
      u: request.url,
    })
      .then((response) => {
        logger.verbose("Plausible server event response", response)
      })
      .catch((error) => {
        logger.error("Plausible server event error", error)
      })
  }
}

/**
 * Add default GET headers and log the request.
 */
async function fetchWrapper(request: Request): Promise<Response> {
  if (request.method === "GET") {
    request.headers.set("Accept", "application/json")
  }

  logger.info(`${request.method} ${request.url}`)

  const isSearchRequest =
    request.url.includes("/v1/images/") || request.url.includes("/v1/audio/")
  if (!isSearchRequest) {
    return fetch(request)
  }

  const requestTime = new Date()
  const response = await fetch(request)
  sendEvent(response, request, requestTime)
  return response
}

export default defineNitroPlugin((nitroApp) => {
  const clientId = import.meta.env.NUXT_API_CLIENT_ID
  const clientSecret = import.meta.env.NUXT_API_CLIENT_SECRET
  const baseUrl = import.meta.env.NUXT_PUBLIC_API_URL

  const credentials =
    clientId && clientSecret ? { credentials: { clientId, clientSecret } } : {}

  const authenticatedOpenverse = createClient({
    baseUrl,
    ...credentials,
    fetch: fetchWrapper,
  })
  logger.info({
    status: "Created Openverse client",
    authenticated: Boolean(credentials.credentials),
    baseUrl,
  })

  // Add authenticated client to the proxied `/api` requests
  nitroApp.hooks.hook("request", async (event) => {
    if (getRequestURL(event).pathname.startsWith("/api")) {
      logger.info({
        status: "Proxying request",
        request: event.path,
      })
      event.context.client = authenticatedOpenverse
    }
  })
})
