/*
 * Small wrapper for localstorage to protect against SSR and permissions
 */

import { warn } from '~/utils/console'

const localStorageExists = () => process.client && window.localStorage !== null

const tryUse = <R>(fn: () => R, def: R) => {
  try {
    return localStorageExists() ? fn() : def
  } catch (e) {
    warn('`localStorage` access denied', e)
    return def
  }
}

const local: typeof localStorage = {
  get length() {
    return tryUse(() => localStorage.length, 0)
  },
  getItem(key: string) {
    return tryUse(() => localStorage.getItem(key), null)
  },
  setItem(key: string, value: string) {
    tryUse(() => localStorage.setItem(key, value), undefined)
  },
  clear() {
    tryUse(() => localStorage.clear(), undefined)
  },
  removeItem(key) {
    tryUse(() => localStorage.removeItem(key), undefined)
  },
  key(index) {
    return tryUse(() => localStorage.key(index), null)
  },
}

export default local
