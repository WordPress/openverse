import { getCurrentInstance } from "vue"

/**
 * Retrieve the name of the component in which
 * the composable is being used.
 */
export const useComponentName = () => {
  const vm = getCurrentInstance()
  return vm?.proxy?.$options.name ?? "Unknown"
}
