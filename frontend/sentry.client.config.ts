import { useRuntimeConfig } from "#imports"

import * as Sentry from "@sentry/nuxt"

import { sentryDataCollection } from "#shared/constants/sentry"

Sentry.init({
  dsn: useRuntimeConfig().public.sentry.dsn,
  environment: useRuntimeConfig().public.sentry.environment,
  release: useRuntimeConfig().public.sentryRelease,
  ignoreErrors: [
    // Can be safely ignored, @see https://github.com/WICG/resize-observer/issues/38
    /ResizeObserver loop limit exceeded/i,
  ],

  tracesSampleRate: 1.0,
  dataCollection: sentryDataCollection,
})
Sentry.setContext("render context", { platform: "client" })
Sentry.setTag("platform", "client")
