import { useNuxtApp } from "#imports"

/**
 * This composable exists to make it easy to mock the i18n context
 * in the composition API in tests
 */
export function useI18n() {
  return useNuxtApp().$i18n
}
