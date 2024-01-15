import { useRuntimeConfig } from "#imports"

import { defineNitroPlugin } from "nitropack/runtime"
import * as Sentry from "@sentry/node"

import { logger } from "~~/server/utils/logger"

export default defineNitroPlugin((nitroApp) => {
  const {
    public: { sentry },
  } = useRuntimeConfig()

  if (import.meta.dev) {
    // Should not need this, but without it Dev builds fail with "The requested module 'vue' does not provide an export named 'computed'"
    // @see https://github.com/getsentry/sentry-javascript/issues/12490
    // @ts-expect-error - globalThis is not defined here, and this is only used in dev mode.
    globalThis._sentryEsmLoaderHookRegistered = true
  }
  Sentry.init({
    dsn: sentry.dsn,
    environment: sentry.environment,
    release: sentry.release,
  })
  Sentry.setContext("render context", { platform: "server" })
  logger.success("Initialized sentry on the server with config\n", sentry)

  nitroApp.hooks.hook("request", (event) => {
    event.context.$sentry = Sentry
  })

  nitroApp.hooks.hookOnce("close", async () => {
    logger.log("Closing Sentry")
    await Sentry.close()
  })
})
