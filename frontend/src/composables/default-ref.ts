import { computed, ref, UnwrapRef } from "vue"

const NotSet = Symbol("NotSet")

/**
 * Produces a `computed` that returns a default value until
 * an explicit value is set.
 *
 * @param getDefault - A function returning the default value
 */
export const defaultRef = <T>(getDefault: () => T) => {
  const explicitlySet = ref<T | typeof NotSet>(NotSet)
  return computed<T>({
    get() {
      if (explicitlySet.value === NotSet) {
        return getDefault()
      }
      return explicitlySet.value as T
    },
    set(v) {
      explicitlySet.value = v as UnwrapRef<T>
    },
  })
}
