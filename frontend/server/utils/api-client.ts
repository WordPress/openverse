import { logger } from "~~/server/utils/logger"

import { userAgentHeader } from "#shared/constants/user-agent.mjs"

import type { FetchResponse } from "ofetch"

const REQUEST_TIMEOUT_MS = 30_000
const EXPIRY_THRESHOLD_SECONDS = 5

interface TokenResponse {
  access_token: string
  expires_in: number
}

export interface ApiCredentials {
  clientId: string
  clientSecret: string
}

export interface OpenverseApiClient {
  /**
   * Sends a GET request to `<apiUrl>v1/<path>`. Resolves with the response
   * for any status code, and rejects only if the request can't be completed.
   */
  get: <T>(
    path: string,
    query?: Record<string, string>
  ) => Promise<FetchResponse<T>>
}

const currTimestamp = () => Math.floor(Date.now() / 1000)

/**
 * Creates the client that Nitro uses to send the proxied requests to the API.
 * With credentials, it requests an access token, refreshes it before it
 * expires, and shares one token request between concurrent requests.
 */
export const createOpenverseApiClient = ({
  apiUrl,
  credentials,
}: {
  apiUrl: string
  credentials?: ApiCredentials
}): OpenverseApiClient => {
  const baseUrl = apiUrl.endsWith("/") ? apiUrl : `${apiUrl}/`
  let token: { value: string; expiry: number } | null = null
  let tokenRequest: Promise<string> | null = null

  const refreshToken = async ({ clientId, clientSecret }: ApiCredentials) => {
    try {
      const res = await $fetch<TokenResponse>(
        `${baseUrl}v1/auth_tokens/token/`,
        {
          method: "POST",
          body: new URLSearchParams({
            client_id: clientId,
            client_secret: clientSecret,
            grant_type: "client_credentials",
          }),
          headers: userAgentHeader,
          timeout: REQUEST_TIMEOUT_MS,
        }
      )
      token = {
        value: res.access_token,
        expiry: currTimestamp() + res.expires_in,
      }
      return token.value
    } catch (error) {
      // Serve this request anonymously, and request a new token on the next one.
      token = null
      logger.error(`Unable to retrieve API token: ${(error as Error).message}`)
      return ""
    }
  }

  const getToken = async () => {
    if (!credentials) {
      return ""
    }
    if (token && token.expiry - EXPIRY_THRESHOLD_SECONDS > currTimestamp()) {
      return token.value
    }
    tokenRequest ??= refreshToken(credentials).finally(() => {
      tokenRequest = null
    })
    return tokenRequest
  }

  return {
    async get<T>(path: string, query: Record<string, string> = {}) {
      const accessToken = await getToken()
      return $fetch.raw(`${baseUrl}v1/${path}`, {
        query,
        headers: {
          ...userAgentHeader,
          Accept: "application/json",
          ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        },
        timeout: REQUEST_TIMEOUT_MS,
        retry: 0,
        ignoreResponseError: true,
      }) as Promise<FetchResponse<T>>
    },
  }
}
