import type {
  ComponentCustomOptions as _ComponentCustomOptions,
  ComponentCustomProperties as _ComponentCustomProperties,
} from "vue"

// Fix until the libraries are updated to correctly augment `vue`.
// See https://nuxt.com/blog/v3-13#vue-typescript-changes
declare module "@vue/runtime-core" {
  // eslint-disable-next-line @typescript-eslint/no-empty-object-type
  interface ComponentCustomProperties extends _ComponentCustomProperties {}
  // eslint-disable-next-line @typescript-eslint/no-empty-object-type
  interface ComponentCustomOptions extends _ComponentCustomOptions {}
}

declare module "#app" {
  interface NuxtApp {
    $captureException: (error: unknown, extra?: Record<string, unknown>) => void
    $captureMessage: (message: string) => void
  }
}

export {}
