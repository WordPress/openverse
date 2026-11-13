import type { OpenverseApiClient } from "~~/server/utils/api-client"

declare module "h3" {
  interface H3EventContext {
    apiClient?: OpenverseApiClient
    internalRequestToken?: string
  }
}

export {}
