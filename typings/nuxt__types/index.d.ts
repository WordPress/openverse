import '@nuxt/types'
import '@nuxtjs/i18n'
import { CookieSerializeOptions } from 'cookie'

import type { OpenverseCookieState } from '~/types/cookies'

import type { Details as UADetails } from 'express-useragent'

export interface SetParams<Key extends keyof OpenverseCookieState> {
  name: Key
  value: OpenverseCookieState[Key]
  opts?: CookieSerializeOptions
}

export interface NuxtCookies {
  set: <Key extends keyof OpenverseCookieState>(
    name: Key,
    value: OpenverseCookieState[Key],
    opts?: CookieSerializeOptions
  ) => void
  setAll: (cookieArray: SetParams[]) => void
  get: <Key extends keyof OpenverseCookieState>(
    name: Key,
    opts?: GetOptions
  ) => OpenverseCookieState[Key]
  getAll: (opts?: GetOptions) => OpenverseCookieState
  remove: <Key extends keyof OpenverseCookieState>(
    name: Key,
    opts?: CookieSerializeOptions
  ) => void
  removeAll: () => void
}

declare module '@nuxt/types' {
  export interface Context {
    $ua: UADetails | null
    $cookies: NuxtCookies
  }
  export interface NuxtAppOptions {
    $ua: UADetails | null
    $cookies: NuxtCookies
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
