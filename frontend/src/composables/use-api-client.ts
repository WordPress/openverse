import { useNuxtApp, useRequestEvent, useRequestFetch } from "#imports"

import { createApiClient } from "~/data/api-service"
import { createProxyClient } from "~/data/proxy-service"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useProviderStore } from "~/stores/provider"

/**
 * Returns the client for the media requests. With the `proxy_requests` flag
 * on, the requests go through the Nuxt server routes, otherwise directly to
 * the API.
 */
export function useApiClient() {
  const featureFlagStore = useFeatureFlagStore()

  const fakeSensitive =
    featureFlagStore.isOn("fake_sensitive") &&
    featureFlagStore.isOn("fetch_sensitive")

  if (featureFlagStore.isOn("proxy_requests")) {
    // During SSR, `useRequestFetch` calls the server routes in-process and
    // forwards the request headers, including the session cookie.
    return createProxyClient({
      requestFetch: useRequestFetch(),
      providerStore: useProviderStore(),
      fakeSensitive,
      internalRequestToken: import.meta.server
        ? useRequestEvent()?.context.internalRequestToken
        : undefined,
    })
  }

  const { $openverseApiToken: accessToken } = useNuxtApp()
  return createApiClient({ accessToken, fakeSensitive })
}
