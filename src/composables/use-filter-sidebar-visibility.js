import { onMounted, ref } from '@nuxtjs/composition-api'

import local from '~/utils/local'
import { isMinScreen } from '~/composables/use-media-query'

/**
 * This global ref is SSR safe because it will only
 * change internal value based on client side interaction.
 *
 * @type {import('@nuxtjs/composition-api').Ref<boolean>}
 */
const isVisible = ref(false)

/**
 * This composable keeps track of whether the filters (sidebar or modal) should be visible.
 * @param {object} props
 * @param {import('@nuxtjs/composition-api').Ref<boolean>} [props.mediaQuery=isMinScreen('md')] - the minimum media query at which
 * the filters are shown as sidebar instead of the full-page modal.
 * @returns {{isVisible: import('@nuxtjs/composition-api').Ref<boolean>, setVisibility: (val: boolean) => void}}
 */
export function useFilterSidebarVisibility({ mediaQuery } = {}) {
  if (!mediaQuery) {
    mediaQuery = isMinScreen('md')
  }
  /**
   * Open or close the filter sidebar
   * @param {boolean} val
   */
  const setVisibility = (val) => {
    isVisible.value = val
    local.set(process.env.filterStorageKey, val)
  }

  onMounted(() => {
    const localFilterState = () =>
      local.get(process.env.filterStorageKey) === 'true'
    setVisibility(mediaQuery.value && localFilterState())
  })

  return {
    isVisible,
    setVisibility,
  }
}
