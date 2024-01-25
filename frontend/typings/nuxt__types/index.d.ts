import type { Plausible } from "plausible-tracker"

declare module "#app" {
  interface NuxtApp {
    $plausible: ReturnType<typeof Plausible>
    $sentry: {
      captureException: (error: Error | unknown, options?: unknown) => void
      captureMessage: (message: string) => void
    }
  }
}

declare module "@nuxtjs/i18n" {
  /**
   * We put a little extra information in the Vue-i18n `locales` field such as the
   * locale's name and native name, which comes in use here.
   */
  export interface LocaleObject {
    name: string
    nativeName: string
    translated: number
  }
}

declare module "nuxt/schema" {
  interface RuntimeConfig {
    apiSecret: string
  }
  interface PublicRuntimeConfig {
    apiUrl: string
    providerUpdateFrequency: number
    savedSearchCount: number
  }
}
