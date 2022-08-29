import { ref } from '@nuxtjs/composition-api'

import { env } from '~/utils/env'
import local from '~/utils/local'

/**
 * This global ref is SSR safe because it will only
 * change internal value based on client side interaction.
 *
 */
const isVisible = ref<boolean>(false)

/**
 * This composable keeps track of whether the filters (sidebar or modal) should be visible.
 */
export const useFilterSidebarVisibility = () => {
  /**
   * Open or close the filter sidebar
   * @param val - whether to set the sidebar visible.
   */
  const setVisibility = (val: boolean) => {
    isVisible.value = val
    local.setItem(env.filterStorageKey, String(val))
  }

  return {
    isVisible,
    setVisibility,
  }
}
