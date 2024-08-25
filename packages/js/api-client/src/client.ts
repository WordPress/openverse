import { Routes, RoutesMeta } from "./generated/routes"
import { OAuth2Token } from "./generated/models"

interface RequestConfig {
  headers: Headers
  method: string
  body?: string | URLSearchParams
}

export interface OpenverseResponse<R extends keyof Routes> {
  body: Routes[R]["response"]
  meta: {
    headers: Headers
    status: number
    url: string
    request: RequestConfig
  }
}

export interface ClientCredentials {
  clientId: string
  clientSecret: string
}

export interface ClientOptions {
  baseUrl?: string
  credentials?: ClientCredentials
}

/**
 * Get the timestamp as the number of seconds from the UNIX epoch.
 * @returns the UNIX timestamp with a resolution of one second
 */
const currTimestamp = (): number => Math.floor(Date.now() / 1e3)
export const EXPIRY_THRESHOLD = 5 // seconds

type OpenverseRequest<R extends keyof Routes> = Routes[R]["request"] & {
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

export class CredentialsError extends Error {
  constructor(context: string) {
    super(
      `'${context}' may only be called on credentialed clients. Instantiate the client with the 'credentials' option to create a credentialed client.`
    )
  }
}

export class OpenverseClient {
  _baseUrl: string
  _credentials: ClientOptions["credentials"]
  _getTransport: () => Promise<Transport>

  _apiToken: OAuth2Token | null = null
  _apiTokenMutex = {
    requesting: false,
    failure: null as unknown,
  }
  _tokenExpiry: number | null = null

  constructor(
    { baseUrl = "https://api.openverse.org/", credentials }: ClientOptions = {},
    getTransport: () => Promise<Transport> = getFetch
  ) {
    this._baseUrl = baseUrl.endsWith("/")
      ? baseUrl.substring(0, baseUrl.length - 1)
      : baseUrl

    this._credentials = credentials
    this._getTransport = getTransport
  }

  /**
   * Perform an Openverse API request, automatically handling
   * the Openverse API authentication process if needed.
   *
   * @param endpoint - An Openverse API endpoint of the pattern `[METHOD] [PATH]`
   * @param req - The path, query, and body parameters for the endpoint, and optionally headers to send with the request
   * @returns A promise resolving to an object with `body` representing the response from the Openverse API, along with additional request metadata including full request and response headers
   */
  async request<R extends keyof Routes>(
    endpoint: R,
    req?: OpenverseRequest<R>
  ): Promise<OpenverseResponse<R>> {
    const request = req ?? ({} as OpenverseRequest<R>)
    request.headers = this._credentials
      ? await this.getAuthHeaders(request.headers)
      : request.headers
    return this._request(endpoint, request)
  }

  /**
   * @returns Whether the instance has credentials and is therefore a credentialed client.
   */
  public isCredentialed(): this is { _credentials: ClientCredentials } {
    return !!this._credentials
  }

  /**
   * Create non-credentialed version of the `OpenverseClient`
   * using the same base URL and transport as the current instance.
   *
   * @returns A non-credentialed `OpenverseClient`
   */
  withoutCredentials(): OpenverseClient {
    return new OpenverseClient({ baseUrl: this._baseUrl }, this._getTransport)
  }

  /**
   * The raw interface to perform a request to the Openverse API.
   *
   * This function **does not** handle authentication. This
   * is intentional and prevents introducing complex circular
   * logic when the client itself makes a request to retrieve
   * the API token for credentialed clients.
   */
  private async _request<R extends keyof Routes>(
    endpoint: R,
    { headers, ...req }: OpenverseRequest<R>
  ): Promise<OpenverseResponse<R>> {
    // eslint-disable-next-line prefer-const
    let [method, url] = endpoint.split(" ")
    const endpointMeta = RoutesMeta[endpoint]

    if (req && endpointMeta.pathParams.length) {
      endpointMeta.pathParams.forEach((param) => {
        if (!(param in req)) {
          throw Error(
            `'${endpoint}' request missing required path parameter '${param}'`
          )
        }
        url = url.replace(`{${param}}`, req[param] as string)
      })
    }

    const transport = await this._getTransport()

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

    const fullUrl = `${this._baseUrl}${url}`
    const response = await transport.fetch(fullUrl, requestConfig)

    const body = endpointMeta.jsonResponse
      ? await transport.getJsonResponseBody(response)
      : await transport.getBinaryResponseBody(response)
    return {
      body: body as Routes[R]["response"],
      meta: {
        headers: response.headers,
        status: response.status,
        url: fullUrl,
        request: requestConfig,
      },
    }
  }

  /**
   * Determine if the current state of the client requires waiting for
   * a token refresh to complete. This is distinct from whether
   * the client should trigger a token refresh, because if an API token
   * already exists, the refresh is eagerly requested before the current
   * token expires. That means that if the request triggering the token refresh
   * happens within the expiry threshold (see `expiryThreshold`), it
   * can proceed with the existing token, as it is still valid.
   *
   * However, if the token is expired (or no token yet exists), the request
   * must be held until the client has an API token.
   *
   * This is only relevant to clients configured with credentials. Non-credentialed
   * clients bypass this process altogether.
   *
   * @returns Whether the client should wait.
   */
  private _mustAwaitTokenRefresh = () =>
    this.isCredentialed() &&
    (!(this._apiToken && this._tokenExpiry) ||
      this._tokenExpiry <= currTimestamp())

  /**
   * Determine if the client requires a new API token, whether due to
   * the lack of a token altogether or due to the existing token's
   * pending expiration.
   *
   * Furthermore, prevent further API token requests if a previous API token
   * request failed.
   *
   * TODO: is that safe?
   *
   * Refer to the documentation on `_mustAwaitTokenRefresh` for further details.
   *
   * @returns Whether the client should trigger a token refresh.
   */
  private _shouldTriggerTokenRefresh = () =>
    this.isCredentialed() &&
    !(this._apiTokenMutex.failure || this._apiTokenMutex.requesting) &&
    (!(this._apiToken && this._tokenExpiry) ||
      this._tokenExpiry - EXPIRY_THRESHOLD < currTimestamp())

  /**
   * Refresh the API token used by credentialed clients.
   *
   * In regular usage, it is not necessary to call this function, as
   * `request` handles this for you automatically.
   *
   * The function is exposed primarily to make debugging the authentication
   * flow easier during development of applications using the API client.
   */
  async refreshAuthentication() {
    if (!this.isCredentialed()) {
      throw new CredentialsError("refreshAuthentication")
    }

    this._apiTokenMutex.requesting = true
    try {
      const tokenResponse = await this._request("POST /v1/auth_tokens/token/", {
        body: {
          grant_type: "client_credentials",
          client_id: this._credentials.clientId,
          client_secret: this._credentials.clientSecret,
        },
      })
      this._tokenExpiry = currTimestamp() + tokenResponse.body.expires_in

      this._apiToken = tokenResponse.body

      // Clear any previous failures, given this request succeeded
      this._apiTokenMutex.failure = null
    } catch (e) {
      console.error("[openverse-api-client]: Token refresh failed!", e)
      // Fall back to `true` if for some reason `e` is falsy.
      this._apiTokenMutex.failure = e || true
      throw e
    } finally {
      this._apiTokenMutex.requesting = false
    }

    return this._apiToken
  }

  /**
   * Wait for the current API token refresh to finish.
   */
  private async _awaitApiToken() {
    // @todo: Maybe change this to some kind of callback registration that `refreshAuthentication`
    // clears instead?
    while (this._apiTokenMutex.requesting) {
      await new Promise((res) => setTimeout(res, 50))
    }
  }

  /**
   * Create a `Headers` object populated with the `Authorization` header
   * required for authenticated Openverse API requests.
   *
   * @param headers - Optional headers into which to merge the `Authorization`
   * @returns `Headers` with a populated `Authorization`
   */
  async getAuthHeaders(headers: HeadersInit = {}): Promise<Headers> {
    if (!this.isCredentialed()) {
      throw new CredentialsError("getAuthHeaders")
    }

    if (this._shouldTriggerTokenRefresh()) {
      this.refreshAuthentication()
    }

    if (this._mustAwaitTokenRefresh()) {
      await this._awaitApiToken()
    }

    const withAuth = new Headers(headers)

    withAuth.append(
      "Authorization",
      `Bearer ${(this._apiToken as Exclude<OAuth2Token, null>).access_token}`
    )
    return withAuth
  }
}
