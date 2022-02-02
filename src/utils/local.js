// Small wrapper for localstorage to protect against SSR and permissions

const localStorageExists = () => process.client && window.localStorage !== null

const local = {
  get(key) {
    return localStorageExists() ? localStorage.getItem(key) : null
  },
  set(key, value) {
    return localStorageExists() ? localStorage.setItem(key, value) : null
  },
}

export default local
