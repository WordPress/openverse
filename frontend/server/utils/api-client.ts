import {
  createClient,
  type ClientCredentials,
  type OpenverseClient,
} from "@openverse/api-client"

import { userAgentHeader } from "#shared/constants/user-agent.mjs"

const REQUEST_TIMEOUT_MS = 30_000

/**
 * Creates the client that Nitro uses to send the proxied requests to the API.
 * With credentials, the client requests the access token and refreshes it
 * before it expires. Requests that take longer than 30 seconds are aborted.
 */
export const createOpenverseApiClient = ({
  apiUrl,
  credentials,
}: {
  apiUrl: string
  credentials?: ClientCredentials
}): OpenverseClient =>
  createClient({
    baseUrl: apiUrl,
    credentials,
    headers: userAgentHeader,
    fetch: (request) =>
      fetch(request, { signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS) }),
  })
