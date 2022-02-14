import '@nuxt/types'
import type { IVueI18n } from 'vue-i18n'
import type { Details as UADetails } from 'express-useragent'

declare module '@nuxt/types' {
  export interface NuxtAppOptions {
    $ua: UADetails
  }
  export interface Context {
    i18n: IVueI18n
  }
}
