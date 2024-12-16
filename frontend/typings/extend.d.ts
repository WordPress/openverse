import type {
  ComponentCustomOptions as _ComponentCustomOptions,
  ComponentCustomProperties as _ComponentCustomProperties,
} from "vue"

import type { Sentry } from "@sentry/node"

// Fix until the libraries are updated to correctly augment `vue`.
// See https://nuxt.com/blog/v3-13#vue-typescript-changes
declare module "@vue/runtime-core" {
  // eslint-disable-next-line @typescript-eslint/no-empty-object-type
  interface ComponentCustomProperties extends _ComponentCustomProperties {}
  // eslint-disable-next-line @typescript-eslint/no-empty-object-type
  interface ComponentCustomOptions extends _ComponentCustomOptions {}
}

declare module "@sentry/nuxt" {
  const Sentry: Sentry
  export = Sentry
}

declare module "#app" {
  interface NuxtApp {
    $captureException: Sentry["captureException"]
    $captureMessage: Sentry["captureMessage"]
  }
}

export {}
