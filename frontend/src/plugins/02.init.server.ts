import { defineNuxtPlugin, useCookie } from "#imports"

import type { OpenverseCookieState } from "#shared/types/cookies"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useUiStore } from "~/stores/ui"

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

  /* UI store */
  const uiStore = useUiStore()
  const uiCookies = useCookie<OpenverseCookieState["ui"]>("ui")
  uiStore.initFromCookies(uiCookies.value ?? {})
})
