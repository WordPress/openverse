import { defineNuxtRouteMiddleware } from "#imports"

import { useFeatureFlagStore } from "~/stores/feature-flag"

/**
 * On every page navigation, update the feature flags from query.
 */
export default defineNuxtRouteMiddleware(async (to) => {
  const featureFlagStore = useFeatureFlagStore()
  featureFlagStore.initFromQuery(to.query)
})
