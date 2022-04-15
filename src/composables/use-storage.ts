import { ref, watch, Ref } from '@nuxtjs/composition-api'

import local from '~/utils/local'

import { useEventListener } from './use-event-listener'

const defaultWindow =
  typeof window === 'undefined' || !('localStorage' in window)
    ? undefined
    : window

export type Serializer<T> = {
  read(v: string): T
  write(v: T): string
}

export const StorageSerializers = Object.freeze({
  boolean: {
    read: (v) => v === 'true',
    write: (v) => String(v),
  } as Serializer<boolean>,
  number: {
    read: (v) => parseFloat(v),
    write: (v) => String(v),
  } as Serializer<number>,
  string: {
    read: (v) => v,
    write: (v) => String(v),
  } as Serializer<string>,
  object: {
    read: (v) => JSON.parse(v),
    write: (v) => JSON.stringify(v),
    // Disable reason: We do actually mean `any` here, not unknown
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  } as Serializer<any>,
} as const)

export type UseStorageOptions<T> = {
  listenToStorageChanges: boolean
  writeDefaults: boolean
  window: Window
  storage: Storage
  serializer: Serializer<T>
  onError: (e: Error) => void
}

const defaultStorageOptions = Object.freeze({
  listenToStorageChanges: true,
  writeDefaults: true,
  window: defaultWindow,
  storage: local,
  serializer: StorageSerializers.object,
  onError: (e) => {
    console.error(e)
  },
} as UseStorageOptions<unknown>)

/**
 * Reactive LocalStorage.
 *
 * @see https://vueuse.org/useStorage
 */
export function useStorage<T>(
  key: string,
  initialValue: T,
  options: Partial<UseStorageOptions<T>> = {}
): Ref<T> {
  const optionsWithDefaults = {
    ...defaultStorageOptions,
    ...options,
  }
  const { listenToStorageChanges, writeDefaults, window, storage, onError } =
    optionsWithDefaults

  const type =
    initialValue == null
      ? 'object'
      : typeof initialValue === 'boolean'
      ? 'boolean'
      : typeof initialValue === 'string'
      ? 'string'
      : typeof initialValue === 'number'
      ? 'number'
      : 'object'

  const data = ref(initialValue) as Ref<T>
  const serializer = options.serializer ?? StorageSerializers[type]

  function read(event?: StorageEvent) {
    if (!storage || (event && event.key !== key)) return

    try {
      const rawValue = event ? event.newValue : storage.getItem(key)
      if (rawValue == null) {
        data.value = initialValue as T
        if (writeDefaults && initialValue !== null)
          storage.setItem(key, serializer.write(initialValue))
      } else {
        data.value = serializer.read(rawValue) as T
      }
    } catch (e) {
      onError(e as Error)
    }
  }

  read()

  if (window && listenToStorageChanges)
    useEventListener(window, 'storage', (e: Event) =>
      setTimeout(() => read(e as StorageEvent), 0)
    )

  if (storage) {
    watch(data, () => {
      try {
        if (data.value == null) storage.removeItem(key)
        else storage.setItem(key, serializer.write(data.value))
      } catch (e) {
        onError(e as Error)
      }
    })
  }

  return data
}
