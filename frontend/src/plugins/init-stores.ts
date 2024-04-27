import { defineNuxtPlugin } from "@nuxtjs/composition-api"

import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useUiStore } from "~/stores/ui"

/**
 * Initialize the feature flag and UI stores from cookies and query parameters on every request.
 */
export default defineNuxtPlugin(async ({ $cookies, $pinia, query }) => {
  /* Feature flag store */
  const featureFlagStore = useFeatureFlagStore($pinia)
  featureFlagStore.initFromCookies($cookies.get("features") ?? {})
  featureFlagStore.initFromCookies($cookies.get("sessionFeatures") ?? {})
  featureFlagStore.initFromQuery(query)

  /* UI store */
  const uiStore = useUiStore($pinia)
  uiStore.initFromCookies($cookies.get("ui") ?? {})
})
