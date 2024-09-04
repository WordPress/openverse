import { ProcessFetchingError } from "~/plugins/errors"
import { SendCustomEvent } from "~/types/analytics"

import type { Sentry } from "@sentry/node"

declare module "@nuxtjs/i18n" {
  /**
   * We put a little extra information in the Vue-i18n `locales` field such as the
   * locale's name and native name, which comes in use here.
   */
  export interface LocaleObject {
    nativeName: string
    translated: number
  }
}

declare module "#app" {
  interface NuxtApp {
    $processFetchingError: ProcessFetchingError
    $sendCustomEvent: SendCustomEvent
    $sentry: Sentry
  }
}

export {}
