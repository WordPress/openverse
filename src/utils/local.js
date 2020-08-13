// Small wrapper for localstorage to protect against SSR

const localStorageExists =
  typeof window !== 'undefined' && 'localStorage' in window

const local = {
  get(key) {
    return localStorageExists ? localStorage.getItem(key) : null
  },
  set(key, value) {
    return localStorageExists ? localStorage.setItem(key, value) : null
  },
}

export default local
