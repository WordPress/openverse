import { defineNuxtPlugin, useRuntimeConfig } from "#imports"

import * as Sentry from "@sentry/vue"

export default defineNuxtPlugin((nuxtApp) => {
  const {
    public: { sentry },
  } = useRuntimeConfig()

  if (!sentry.dsn) {
    console.warn("Sentry DSN wasn't provided")
  }

  Sentry.init({
    dsn: sentry.dsn,
    environment: sentry.environment,
    app: nuxtApp.vueApp,
  })
  Sentry.setContext("render context", { platform: "client" })

  return {
    provide: {
      sentry: Sentry,
    },
  }
})
