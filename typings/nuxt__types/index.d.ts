import '@nuxt/types'
import '@nuxtjs/i18n'
import type { Details as UADetails } from 'express-useragent'

declare module '@nuxt/types' {
  export interface Context {
    $ua: UADetails | null
  }
  export interface NuxtAppOptions {
    $ua: UADetails | null
  }
}

declare module '@nuxtjs/i18n' {
  /**
   * We put a little extra information in the Vue-i18n `locales` field such as the
   * locale's name and native name, which comes in use here.
   */
  export interface LocaleObject {
    name: string
    nativeName: string
  }
}
