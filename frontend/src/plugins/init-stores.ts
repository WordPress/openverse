import { defineNuxtPlugin, useCookie } from "#imports"

import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useUiStore } from "~/stores/ui"
import { useProviderStore } from "~/stores/provider"

import type { OpenverseCookieState } from "~/types/cookies"

/**
 * Initialize the feature flag and UI stores from cookies and query parameters.
 */
export default defineNuxtPlugin(async () => {
  /* Provider store */
  const providerStore = useProviderStore()
  await providerStore.fetchProviders()

  /* Feature flag store */
  const featureFlagStore = useFeatureFlagStore()
  const featureCookies = useCookie<OpenverseCookieState["features"]>("features")
  featureFlagStore.initFromCookies(featureCookies.value ?? {})
  const sessionFeatures =
    useCookie<OpenverseCookieState["sessionFeatures"]>("sessionFeatures")
  featureFlagStore.initFromCookies(sessionFeatures.value ?? {})

  /* UI store */
  const uiStore = useUiStore()
  const uiCookies = useCookie<OpenverseCookieState["ui"]>("ui")
  uiStore.initFromCookies(uiCookies.value ?? {})
})
