import { defineNuxtMiddleware } from "@nuxtjs/composition-api"

import { useProviderStore } from "~/stores/provider"

/**
 * On every page navigation, update the media providers if necessary.
 */
export default defineNuxtMiddleware(async ({ $pinia }) => {
  const providerStore = useProviderStore($pinia)
  await providerStore.updateProvidersIfNeeded()
})
