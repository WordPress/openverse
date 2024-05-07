import { defineNuxtMiddleware } from "@nuxtjs/composition-api"

import { useFeatureFlagStore } from "~/stores/feature-flag"

/**
 * On every page navigation, update the feature flags from query.
 */
export default defineNuxtMiddleware(async ({ $pinia, query }) => {
  const featureFlagStore = useFeatureFlagStore($pinia)
  featureFlagStore.initFromQuery(query)
})
