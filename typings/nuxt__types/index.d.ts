import '@nuxt/types'
import type { Details as UADetails } from 'express-useragent'

declare module '@nuxt/types' {
  export interface Context {
    $ua: UADetails | null
  }
  export interface NuxtAppOptions {
    $ua: UADetails | null
  }
}
