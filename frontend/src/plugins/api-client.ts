import { OpenverseClient } from "@openverse/api-client"

import type { Plugin, Context } from "@nuxt/types"

let client: OpenverseClient | null = null

declare module "@nuxt/types" {
  interface Context {
    $apiClient: OpenverseClient
  }
}

const getCredentials = ({
  $config: { apiClientId, apiClientSecret },
}: Context) => {
  if (apiClientId && apiClientSecret) {
    return { clientId: apiClientId, clientSecret: apiClientSecret }
  }
  return undefined
}

export default (async function apiClient(context, inject) {
  if (client === null) {
    client = OpenverseClient({
      baseUrl: process.env.API_URL,
      credentials: getCredentials(context),
    })
  }

  inject("apiClient", client)
} satisfies Plugin)
