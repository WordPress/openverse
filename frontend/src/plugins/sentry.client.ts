import { defineNuxtPlugin } from "#imports"

import * as Sentry from "@sentry/nuxt"

export default defineNuxtPlugin(() => {
  const { captureException, captureMessage } = Sentry
  return {
    provide: {
      captureException,
      captureMessage,
    },
  }
})
