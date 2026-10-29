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

  tracesSampleRate: 1.0,
  dataCollection: sentryDataCollection,
})
Sentry.setContext("render context", { platform: "server" })
Sentry.setTag("platform", "server")
