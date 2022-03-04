/*
 * Small wrapper for localstorage to protect against SSR and permissions
 */

import { warn } from '~/utils/console'

const localStorageExists = () => process.client && window.localStorage !== null

const local = {
  get(key: string) {
    try {
      return localStorageExists() ? localStorage.getItem(key) : null
    } catch (e) {
      // Probably a `SecurityError`
      warn('`localStorage` access denied', e)
      return null
    }
  },
  set(key: string, value: string) {
    try {
      if (localStorageExists()) localStorage.setItem(key, value)
    } catch (e) {
      // Probably a `SecurityError`
      warn('`localStorage` access denied', e)
    }
  },
}

export default local
