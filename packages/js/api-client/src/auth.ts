import type { Middleware } from "openapi-fetch"

import type { components } from "./generated/openverse"

import type { OpenverseClient, ClientCredentials } from "./types"

type OAuth2Token = components["schemas"]["OAuth2Token"]

const currTimestamp = (): number => Math.floor(Date.now() / 1e3)
export const EXPIRY_THRESHOLD = 5 // seconds

export class OpenverseAuthMiddleware implements Middleware {
  client: OpenverseClient
  credentials: ClientCredentials
  apiToken: OAuth2Token | null = null
  requesting = false
  failure = null as unknown
  tokenExpiry: number | null = null

  constructor(client: OpenverseClient, credentials: ClientCredentials) {
    this.client = client
    this.credentials = credentials
  }

  onRequest: Middleware["onRequest"] = async ({ schemaPath, request }) => {
    if (schemaPath == "/v1/auth_tokens/token/") {
      // Do not send auth headers for token generation requests
      return request
    }

    const apiToken = await this.getApiToken()
    request.headers.set("Authorization", `Bearer ${apiToken}`)
    return request
  }

  /**
   * Get the timestamp as the number of seconds from the UNIX epoch.
   * @returns the UNIX timestamp with a resolution of one second
   */
  get currTimestamp() {
    return Math.floor(Date.now() / 1e3)
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
  private mustAwaitTokenRefresh = () =>
    !(this.apiToken && this.tokenExpiry) || this.tokenExpiry <= currTimestamp()

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
   * Refer to the documentation on `mustAwaitTokenRefresh` for further details.
   *
   * @returns Whether the client should trigger a token refresh.
   */
  private shouldTriggerTokenRefresh = () =>
    !(this.failure || this.requesting) &&
    (!(this.apiToken && this.tokenExpiry) ||
      this.tokenExpiry - EXPIRY_THRESHOLD < currTimestamp())

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
    this.requesting = true
    try {
      const tokenResponse = await this.client.POST("/v1/auth_tokens/token/", {
        body: {
          grant_type: "client_credentials",
          client_id: this.credentials.clientId,
          client_secret: this.credentials.clientSecret,
        },
      })

      if (tokenResponse.error) {
        throw tokenResponse.error
      }

      this.tokenExpiry = currTimestamp() + tokenResponse.data.expires_in

      this.apiToken = tokenResponse.data

      // Clear any previous failures, given this request succeeded
      this.failure = null
    } catch (e) {
      console.error("[openverse-api-client]: Token refresh failed!", e)
      // Fall back to `true` if for some reason `e` is falsy.
      this.failure = e || true
      throw e
    } finally {
      this.requesting = false
    }

    return this.apiToken
  }

  /**
   * Wait for the current API token refresh to finish.
   */
  private async awaitApiToken() {
    // @todo: Maybe change this to some kind of callback registration that `refreshAuthentication`
    // clears instead?
    while (this.requesting) {
      await new Promise((res) => setTimeout(res, 50))
    }
  }

  /**
   * Retrieve the Openverse API token for the configured credentials.
   *
   * If necessary (due to non-existence, expiration, or pending expiration),
   * and if not already underway, trigger the retrieval of a new API token.
   * If there is no current usable API token, then wait for the in progress
   * API token request to resolve.
   *
   * @returns Openverse API token
   */
  async getApiToken(): Promise<string> {
    if (this.shouldTriggerTokenRefresh()) {
      this.refreshAuthentication()
    }

    if (this.mustAwaitTokenRefresh()) {
      await this.awaitApiToken()
    }

    if (!this.apiToken) {
      throw new Error(
        "Failed to retrieve Openverse API token for credentialed client. Check logs for details."
      )
    }

    return this.apiToken.access_token
  }
}
