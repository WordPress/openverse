import '@nuxt/types'
import type { IVueI18n } from 'vue-i18n'

declare module '@nuxt/types' {
  export interface Context {
    i18n: IVueI18n
  }
}
