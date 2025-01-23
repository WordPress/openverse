import { defineNuxtPlugin } from "#imports"

import { useProviderStore } from "~/stores/provider"

/**
 * Initialize the provider store on SSR request.
 * This plugin should run after the error and analytics plugins were set up.
 */
export default defineNuxtPlugin(async () => {
  /* Provider store */
  const providerStore = useProviderStore()
  await providerStore.fetchProviders()
})
