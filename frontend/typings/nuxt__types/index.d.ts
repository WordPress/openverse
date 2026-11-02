import type { Locale } from "vue-i18n"

declare module "@nuxtjs/i18n" {
  /**
   * We put a little extra information in the Vue-i18n `locales` field such as the
   * locale's name and native name, which comes in use here.
   */
  // Type parameters must match the original declaration for interface merging.
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  export interface LocaleObject<T = Locale> {
    nativeName: string
    translated: number
  }
}

export {}
