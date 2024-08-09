import { defineNuxtPlugin, useCookie } from "#imports"

import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useUiStore } from "~/stores/ui"
import { useProviderStore } from "~/stores/provider"

import type { OpenverseCookieState } from "~/types/cookies"

/**
 * Initialize the feature flag, ui and provider stores.
 * This plugin should run before all other plugins to
 * ensure that the store states are ready for other plugins.
 */
export default defineNuxtPlugin(async () => {
  /* Feature flag store */
  // Feature flag store uses deploymentEnv variable from the runtimeContext,
  // and should be the first to initialize. Otherwise, the `[nuxt]` context
  // is not available` error is thrown.
  const featureFlagStore = useFeatureFlagStore()

  const featureCookies = useCookie<OpenverseCookieState["features"]>("features")
  featureFlagStore.initFromCookies(featureCookies.value ?? {})

  const sessionFeatures =
    useCookie<OpenverseCookieState["sessionFeatures"]>("sessionFeatures")
  featureFlagStore.initFromCookies(sessionFeatures.value ?? {})

  /* Provider store */
  const providerStore = useProviderStore()
  await providerStore.fetchProviders()

  /* UI store */
  const uiStore = useUiStore()
  const uiCookies = useCookie<OpenverseCookieState["ui"]>("ui")
  uiStore.initFromCookies(uiCookies.value ?? {})
})
