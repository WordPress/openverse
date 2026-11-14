import { defineNuxtRouteMiddleware, navigateTo, useNuxtApp } from "#imports"

import { getUnsupportedLocaleRedirect } from "#shared/utils/unsupported-locale"
import { useUiStore } from "~/stores/ui"

import type { LocaleObject } from "@nuxtjs/i18n"


/**
 * A locale-shaped prefix we don't support (e.g. `/cn`) matches no route, so we
 * redirect it to the English equivalent and show a one-time banner about the
 * missing translation.
 *
 * The redirect sets a persisted flag so it survives the server-side 302. The
 * landing page shows the banner and clears the flag. Any later navigation hides
 * it. So the banner shows once, and only another redirect brings it back.
 */
export default defineNuxtRouteMiddleware((to) => {
  const nuxtApp = useNuxtApp()
  const uiStore = useUiStore()
  const i18n = nuxtApp.$i18n

  // Full configured locale set, not `availableLocales`, which only reflects
  // lazily-loaded message bundles.
  const supportedCodes: string[] = (i18n.locales.value as LocaleObject[]).map(
    (l) => l.code
  )

  // Only consider paths that redirect to a 404
  if (to.matched.length === 0) {
    const newPath = getUnsupportedLocaleRedirect(to.path, supportedCodes)
    if (newPath !== null) {
      uiStore.setUnsupportedLocaleRedirect(true)
      return navigateTo({ path: newPath, query: to.query, hash: to.hash })
    }
  }

  if (uiStore.unsupportedLocaleRedirect) {
    // This is the page the visitor landed on straight after the redirect above.
    // Show the banner once and consume the carrier so it can't re-show later.
    uiStore.setUnsupportedLocaleBannerVisible(true)
    uiStore.setUnsupportedLocaleRedirect(false)
  } else if (!nuxtApp.isHydrating) {
    // Once the visitor navigates somewhere else, hide the banner.
    uiStore.setUnsupportedLocaleBannerVisible(false)
  }
})
