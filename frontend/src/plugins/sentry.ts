import { defineNuxtPlugin, useRuntimeConfig } from "#imports"

import * as Sentry from "@sentry/vue"

export default defineNuxtPlugin((nuxtApp) => {
  const {
    public: { sentry },
  } = useRuntimeConfig()

  if (!sentry.dsn) {
    return
  }

  Sentry.init({
    app: nuxtApp.vueApp,
    dsn: sentry.dsn,
    environment: sentry.environment,
    release: sentry.release,
    // Only allow errors that come from openverse.org or a subdomain
    allowUrls: [/^https?:\/\/((.*)\.)?openverse\.org/],
    ignoreErrors: [
      // Ignore browser extension errors
      /window\.bannerNight/,
      /mce-visual-caret-hidden/,

      // Ignore errant focus-trap-vue errors
      /`initialFocus` did not return a node/,

      // Ignore ResizeObserver loop-related errors
      /ResizeObserver loop limit exceeded/,
      /ResizeObserver loop completed with undelivered notifications/,

      // Cloudflare
      /sendBeacon/,

      // Local errors
      /__webpack_hmr\/modern/,
    ],
  })

  return {
    provide: {
      sentry: Sentry,
    },
  }
})
