import { ref, unref, watch } from '@nuxtjs/composition-api'
import { useEventListener } from '~/composables/use-event-listener'

const defaultWindow =
  typeof window === 'undefined' || !('localStorage' in window)
    ? undefined
    : window

/** @typedef {{read: (function(string): T), write: (function(T): string)}} Serializer<T> */

export const StorageSerializers = {
  boolean: {
    read: (v) => v === 'true',
    write: (v) => String(v),
  },
  any: {
    read: (v) => v,
    write: (v) => String(v),
  },
  string: {
    read: (v) => v,
    write: (v) => String(v),
  },
  object: {
    read: (v) => JSON.parse(v),
    write: (v) => JSON.stringify(v),
  },
}

/**
 * Merges the options with the result of getDefaults.
 * If an error occurs during this process, it will return `null`
 * @template T
 * @param {T} options
 * @param {() => T} getDefaults
 * @returns {T | null}
 */
const useSafeDefaultOptions = (options, getDefaults) => {
  try {
    return {
      ...getDefaults(),
      ...options,
    }
  } catch (e) {
    console.error(e)
    return null
  }
}

/**
 * Reactive LocalStorage.
 *
 * @see https://vueuse.org/useStorage
 * @param {string} key
 * @param {MaybeRef<T>} initialValue
 * @param options
 */
export function useStorage(key, initialValue, options = {}) {
  const optionsWithDefaults = useSafeDefaultOptions(options, () => ({
    listenToStorageChanges: true,
    writeDefaults: true,
    window: defaultWindow,
    storage: defaultWindow?.localStorage,
    onError: (e) => {
      console.error(e)
    },
  }))

  if (optionsWithDefaults === null) {
    return ref(initialValue)
  }

  const { listenToStorageChanges, writeDefaults, window, storage, onError } =
    optionsWithDefaults

  const rawInit = unref(initialValue)

  const type =
    rawInit == null
      ? 'any'
      : typeof rawInit === 'boolean'
      ? 'boolean'
      : typeof rawInit === 'string'
      ? 'string'
      : 'any'

  const data = ref(initialValue)
  const serializer = options.serializer ?? StorageSerializers[type]

  function read(event) {
    if (!storage || (event && event.key !== key)) return

    try {
      const rawValue = event ? event.newValue : storage.getItem(key)
      if (rawValue == null) {
        data.value = rawInit
        if (writeDefaults && rawInit !== null)
          storage.setItem(key, serializer.write(rawInit))
      } else {
        data.value = serializer.read(rawValue)
      }
    } catch (e) {
      onError(e)
    }
  }

  read()

  if (window && listenToStorageChanges)
    useEventListener(window, 'storage', (e) => setTimeout(() => read(e), 0))

  if (storage) {
    watch(data, () => {
      try {
        if (data.value == null) storage.removeItem(key)
        else storage.setItem(key, serializer.write(data.value))
      } catch (e) {
        onError(e)
      }
    })
  }

  return data
}
