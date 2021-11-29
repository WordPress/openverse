import { useContext } from '@nuxtjs/composition-api'

/**
 * This composable exists to make it easy to mock the i18n context
 * in the composition API in tests
 */
export function useI18n() {
  return useContext().i18n
}
