import { onMounted, readonly, ref } from '@nuxtjs/composition-api'
import local from '~/utils/local'

const isFilterSidebarVisible = ref(false)

export function useFilterSidebarVisibility({ mediaQuery }) {
  /**
   * Open or close the filter sidebar
   * @param {boolean} val
   */
  const setFilterSidebarVisibility = (val) => {
    isFilterSidebarVisible.value = val
    local.set(process.env.filterStorageKey, val)
  }

  onMounted(() => {
    const localFilterState = () =>
      local.get(process.env.filterStorageKey) === 'true'
    setFilterSidebarVisibility(mediaQuery && localFilterState())
  })

  return {
    isFilterSidebarVisible: readonly(isFilterSidebarVisible),
    setFilterSidebarVisibility,
  }
}
