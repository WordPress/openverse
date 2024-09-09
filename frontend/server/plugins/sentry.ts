import { useRuntimeConfig, useAppConfig } from "#imports"

import { defineNitroPlugin } from "nitropack/runtime"
import * as Sentry from "@sentry/node"

import { logger } from "~~/server/utils/logger"

export default defineNitroPlugin((nitroApp) => {
  const {
    public: { sentry },
  } = useRuntimeConfig()

  const appConfig = useAppConfig()

  const sentryConfig = {
    dsn: sentry.dsn,
    environment: sentry.environment,
    release: appConfig.semanticVersion,
  }

  Sentry.init(sentryConfig)

  Sentry.setContext("render context", { platform: "server" })
  logger.success("Initialized sentry on the server with config\n", sentryConfig)

  nitroApp.hooks.hook("request", (event) => {
    event.context.$sentry = Sentry
  })

  nitroApp.hooks.hookOnce("close", async () => {
    logger.log("Closing Sentry")
    await Sentry.close()
  })
})
