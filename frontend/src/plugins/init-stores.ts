import { defineNuxtPlugin } from "@nuxtjs/composition-api"

import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useUiStore } from "~/stores/ui"
import { useProviderStore } from "~/stores/provider"

/**
 * Initialize the feature flag and UI stores from cookies and query parameters on every request.
 */
export default defineNuxtPlugin(async ({ $cookies, $pinia }) => {
  /* Provider store */
  const providerStore = useProviderStore($pinia)
  await providerStore.fetchProviders()

  /* Feature flag store */
  const featureFlagStore = useFeatureFlagStore($pinia)
  featureFlagStore.initFromCookies($cookies.get("features") ?? {})
  featureFlagStore.initFromCookies($cookies.get("sessionFeatures") ?? {})

  /* UI store */
  const uiStore = useUiStore($pinia)
  uiStore.initFromCookies($cookies.get("ui") ?? {})
})
