// Small wrapper for localstorage to protect against SSR and permissions

const localStorageExists = () => process.client && window.localStorage !== null

const local = {
  /**
   * @param {Parameters<typeof localStorage['getItem']>} args
   */
  get(...args) {
    try {
      return localStorageExists() ? localStorage.getItem(...args) : null
    } catch (e) {
      // Probably a `SecurityError`
      console.warn('`localStorage` access denied', e)
      return null
    }
  },
  /**
   * @param {Parameters<typeof localStorage['setItem']>} args
   * @return {void}
   */
  set(...args) {
    try {
      if (localStorageExists()) localStorage.setItem(...args)
    } catch (e) {
      // Probably a `SecurityError`
      console.warn('`localStorage` access denied', e)
    }
  },
}

export default local
