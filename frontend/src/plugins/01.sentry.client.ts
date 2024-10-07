import { defineNuxtPlugin, useRuntimeConfig, useAppConfig } from "#imports"

import * as Sentry from "@sentry/vue"

export default defineNuxtPlugin((nuxtApp) => {
  const {
    public: { sentry },
  } = useRuntimeConfig()

  const { semanticVersion } = useAppConfig()

  if (!sentry.dsn) {
    console.warn("Sentry DSN wasn't provided")
  }

  Sentry.init({
    dsn: sentry.dsn,
    environment: sentry.environment,
    release: semanticVersion,
    app: nuxtApp.vueApp,
    ignoreErrors: [
      // Can be safely ignored, @see https://github.com/WICG/resize-observer/issues/38
      /ResizeObserver loop limit exceeded/i,
    ],
  })
  Sentry.setContext("render context", { platform: "client" })

  return {
    provide: {
      sentry: Sentry,
    },
  }
})
