import { createHmac } from "node:crypto"

import {
  createClient,
  type ClientCredentials,
  type OpenverseClient,
} from "@openverse/api-client"

import { userAgentHeader } from "#shared/constants/user-agent.mjs"

const REQUEST_TIMEOUT_MS = 30_000

export const SIGNATURE_TIMESTAMP_HEADER = "x-ov-cf-timestamp"
export const SIGNATURE_MAC_HEADER = "x-ov-cf-mac"

/**
 * Returns the headers that let the API's Cloudflare rules skip the request:
 * the Unix timestamp in seconds and the HMAC-SHA256 of the path, query and
 * timestamp, encoded as base64url. Cloudflare checks the MAC with
 * `is_timed_hmac_valid_v0`, using the same scheme as the k6 load tests.
 */
export const getSignatureHeaders = (
  url: string,
  secret: string,
  now = Date.now()
) => {
  const { pathname, search } = new URL(url)
  const timestamp = Math.floor(now / 1000).toString()
  const mac = createHmac("sha256", secret)
    .update(`${pathname}${search}${timestamp}`)
    .digest("base64url")
  return {
    [SIGNATURE_TIMESTAMP_HEADER]: timestamp,
    [SIGNATURE_MAC_HEADER]: mac,
  }
}

/**
 * Creates the client that Nitro uses to send the proxied requests to the API.
 * With credentials, the client requests the access token and refreshes it
 * before it expires. With a signing secret, every request, including the
 * token requests, is signed. Requests that take longer than 30 seconds are
 * aborted.
 */
export const createOpenverseApiClient = ({
  apiUrl,
  credentials,
  signingSecret,
}: {
  apiUrl: string
  credentials?: ClientCredentials
  signingSecret?: string
}): OpenverseClient =>
  createClient({
    baseUrl: apiUrl,
    credentials,
    headers: userAgentHeader,
    fetch: (request) => {
      const headers = new Headers(request.headers)
      if (signingSecret) {
        for (const [name, value] of Object.entries(
          getSignatureHeaders(request.url, signingSecret)
        )) {
          headers.set(name, value)
        }
      }
      return fetch(request, {
        headers,
        signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS),
      })
    },
  })
