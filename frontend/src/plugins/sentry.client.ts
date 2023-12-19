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
  })
  /**
   * adds render context to the error event that is sent to sentry
   */

  Sentry.setContext("render context", {
    platform: process.client ? "client" : "server",
  })

  return {
    provide: {
      sentry: Sentry,
    },
  }
})
