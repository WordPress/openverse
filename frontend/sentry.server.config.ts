import * as Sentry from "@sentry/nuxt"
import dotenv from "dotenv"

import { sentryDataCollection } from "#shared/constants/sentry"

// Necessary for loading environment variables before Nuxt is loaded
// @see the section on server setup: https://nuxt.com/modules/sentry
dotenv.config()

Sentry.init({
  dsn: process.env.NUXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NUXT_PUBLIC_SENTRY_ENVIRONMENT,
  release: process.env.SEMANTIC_VERSION,

  tracesSampleRate: Number(
    process.env.NUXT_PUBLIC_SENTRY_TRACES_SAMPLE_RATE ?? 0.05
  ),
  dataCollection: sentryDataCollection,
})
Sentry.setContext("render context", { platform: "server" })
Sentry.setTag("platform", "server")
