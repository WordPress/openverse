import { Routes, RoutesMeta } from "./generated/routes"

interface RequestConfig {
  headers: Headers
  method: string
  body?: string | URLSearchParams
}

export interface OpenverseResponse<Body> {
  body: Body
  meta: {
    headers: Headers
    status: number
    url: string
    request: RequestConfig
  }
}

export interface ClientOptions {
  baseUrl?: string
  credentials?: {
    clientId: string
    clientSecret: string
  }
}

/**
 * Get the timestamp as the number of seconds from the UNIX epoch.
 * @returns the UNIX timestamp with a resolution of one second
 */
const currTimestamp = (): number => Math.floor(Date.now() / 1e3)
export const expiryThreshold = 5 // seconds

type OpenverseRequest<T extends keyof Routes> = Routes[T]["request"] & {
  headers?: HeadersInit
}

interface TransportFetchResponse {
  headers: Headers
  status: number
}

export interface Transport {
  fetch: (
    url: string,
    request: RequestConfig
  ) => Promise<TransportFetchResponse>
  getBinaryResponseBody: (res: unknown) => Promise<ArrayBuffer>
  getJsonResponseBody: (res: unknown) => Promise<unknown>
}

async function getFetch(): Promise<Transport> {
  if (!globalThis.fetch) {
    throw new Error(
      "Default fetch transport used outside context with global fetch"
    )
  }

  return {
    fetch,
    getBinaryResponseBody: (res) => (res as Response).arrayBuffer(),
    getJsonResponseBody: (res) => (res as Response).json(),
  }
}

export type OpenverseClient = ReturnType<typeof OpenverseClient>
export const OpenverseClient = (
  {
    baseUrl = "https://api.openverse.engineering/",
    credentials,
  }: ClientOptions = {},
  getTransport: () => Promise<Transport> = getFetch
) => {
  let apiToken: Routes["POST /v1/auth_tokens/token/"]["response"] | null = null

  const apiTokenMutex = {
    requesting: false,
  }

  let tokenExpiry: number | null = null

  const normalisedBaseUrl = baseUrl.endsWith("/")
    ? baseUrl.substring(0, baseUrl.length - 1)
    : baseUrl

  const baseRequest = async <T extends keyof Routes>(
    endpoint: T,
    { headers, ...req }: OpenverseRequest<T>
  ): Promise<OpenverseResponse<Routes[T]["response"]>> => {
    // eslint-disable-next-line prefer-const
    let [method, url] = endpoint.split(" ")
    const endpointMeta = RoutesMeta[endpoint]

    if (req && endpointMeta.pathParams.length) {
      endpointMeta.pathParams.forEach((param) => {
        url = url.replace(`{${param}}`, (req as { [param]: string })[param])
      })
    }

    const transport = await getTransport()

    const finalHeaders = new Headers(headers)
    if (!finalHeaders.has("content-type")) {
      finalHeaders.set("content-type", endpointMeta.contentType)
    }

    const requestConfig: RequestConfig = {
      method,
      headers: finalHeaders,
    }

    if (method === "POST" && "body" in req) {
      if (finalHeaders.get("content-type") == "application/json") {
        requestConfig["body"] = JSON.stringify(req.body)
      } else {
        const form = new URLSearchParams()
        Object.entries(req.body as Record<string, unknown>).forEach(
          ([key, value]) => {
            form.set(key, String(value))
          }
        )
        requestConfig["body"] = form
      }
    } else if ("params" in req) {
      const search = new URLSearchParams(req.params as Record<string, string>)
      if (search.size != 0) {
        url = `${url}?${search}`
      }
    }

    const fullUrl = `${normalisedBaseUrl}${url}`
    const response = await transport.fetch(fullUrl, requestConfig)

    const body = endpointMeta.jsonResponse
      ? await transport.getJsonResponseBody(response)
      : await transport.getBinaryResponseBody(response)
    return {
      body: body as Routes[T]["response"],
      meta: {
        headers: response.headers,
        status: response.status,
        url: fullUrl,
        request: requestConfig,
      },
    }
  }

  const cannotProceedWithoutToken = () =>
    credentials &&
    (!(apiToken && tokenExpiry) || tokenExpiry <= currTimestamp())

  const shouldTriggerTokenRefresh = () =>
    credentials &&
    !apiTokenMutex.requesting &&
    (!(apiToken && tokenExpiry) ||
      tokenExpiry - expiryThreshold < currTimestamp())

  const refreshApiToken = async () => {
    apiTokenMutex.requesting = true
    try {
      const tokenResponse = await baseRequest("POST /v1/auth_tokens/token/", {
        body: {
          grant_type: "client_credentials",
          client_id: (credentials as Exclude<typeof credentials, undefined>)
            .clientId,
          client_secret: (credentials as Exclude<typeof credentials, undefined>)
            .clientSecret,
        },
      })
      tokenExpiry = currTimestamp() + tokenResponse.body.expires_in

      apiToken = tokenResponse.body
    } catch (e) {
      console.error("[openverse-api-client]: Token refresh failed!", e)
    }
    apiTokenMutex.requesting = false
  }

  const awaitApiToken = async () => {
    while (apiTokenMutex.requesting) {
      await new Promise((res) => setTimeout(res, 300))
    }
  }

  const getAuthHeaders = async (headers: HeadersInit): Promise<Headers> => {
    if (!credentials) {
      return new Headers(headers)
    }

    if (shouldTriggerTokenRefresh()) {
      refreshApiToken()
    }

    if (cannotProceedWithoutToken()) {
      await awaitApiToken()
    }

    const withAuth = new Headers(headers)

    withAuth.append(
      "Authorization",
      `Bearer ${(apiToken as Exclude<typeof apiToken, null>).access_token}`
    )
    return withAuth
  }

  const request = async <T extends keyof Routes>(
    endpoint: T,
    req?: OpenverseRequest<T>
  ): Promise<OpenverseResponse<Routes[T]["response"]>> => {
    const authHeaders = await getAuthHeaders(req?.headers ?? {})
    return baseRequest(endpoint, {
      ...(req ?? {}),
      headers: authHeaders,
    } as OpenverseRequest<T>)
  }

  return request
}
