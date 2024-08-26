import type { Client } from "openapi-fetch"

import type { paths } from "./generated/openverse"

export type { components } from "./generated/openverse"

export type OpenverseClient = Client<paths>

export interface ClientCredentials {
  clientId: string
  clientSecret: string
}
