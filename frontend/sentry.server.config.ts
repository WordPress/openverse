import * as Sentry from "@sentry/nuxt"
import dotenv from "dotenv"

// Necessary for loading environment variables before Nuxt is loaded
// @see the section on server setup: https://nuxt.com/modules/sentry
dotenv.config()

console.log(
  "Will initialize Sentry with dsn",
  process.env.NUXT_PUBLIC_SENTRY_DSN
)
console.log("environment", process.env.NUXT_PUBLIC_SENTRY_ENVIRONMENT)
console.log("release", process.env.SEMANTIC_VERSION)

Sentry.init({
  dsn: process.env.NUXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NUXT_PUBLIC_SENTRY_ENVIRONMENT,
  release: process.env.SEMANTIC_VERSION,

  tracesSampleRate: 1.0,
})
Sentry.setContext("render context", { platform: "server" })
