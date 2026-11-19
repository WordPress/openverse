import { defineNuxtPlugin, useCookie, useRuntimeConfig } from "#imports"

import { ensureSession, getSessionConfig } from "#shared/utils/session"
import type { OpenverseCookieState } from "#shared/types/cookies"
import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useUiStore } from "~/stores/ui"

/**
 * Initialize the feature flag, ui and provider stores.
 * This plugin should run before all other plugins to
 * ensure that the store states are ready for other plugins.
 */
export default defineNuxtPlugin(async (nuxtApp) => {
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

  /* Session */
  // The anonymous session lets the Nitro rate limits count the requests of
  // people who share an IP address separately. `ensureSession` sets a new
  // session cookie if the request has no valid session, or an old one.
  const event = nuxtApp.ssrContext?.event
  const config = useRuntimeConfig()
  const sessionConfig = getSessionConfig(
    config.hmacSigningSecret,
    config.public.deploymentEnv
  )
  if (event && sessionConfig) {
    await ensureSession(event, sessionConfig)
  }
})
