import _createClient, {
  type ClientOptions as _ClientOptions,
} from "openapi-fetch"

import { paths } from "./generated/openverse"

import { OpenverseAuthMiddleware } from "./auth"

import type { ClientCredentials, OpenverseClient } from "./types"

export interface ClientOptions
  extends Partial<Pick<_ClientOptions, "baseUrl" | "fetch" | "headers">> {
  credentials?: ClientCredentials
}

export const createClient = ({
  baseUrl = "https://api.openverse.org/",
  credentials,
  ...options
}: ClientOptions = {}): OpenverseClient => {
  options.headers = new Headers(
    (options.headers as Record<string, string>) ?? {}
  )
  if (!options.headers.has("user-agent")) {
    options.headers.set(
      "user-agent",
      `OpenverseAPIClient; https://docs.openverse.org/packages/js/api_client/index.html`
    )
  }

  const client = _createClient<paths>({ baseUrl, ...options })
  if (credentials) {
    client.use(new OpenverseAuthMiddleware(client, credentials))
  }
  return client
}
