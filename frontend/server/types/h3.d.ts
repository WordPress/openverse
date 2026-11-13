import type { OpenverseClient } from "@openverse/api-client"

declare module "h3" {
  interface H3EventContext {
    apiClient?: OpenverseClient
    internalRequestToken?: string
  }
}

export {}
