import { isMinScreen } from '~/composables/use-media-query'
import { useFilterSidebarVisibility } from '~/composables/use-filter-sidebar-visibility'
import { Focus, focusIn } from '~/utils/focus-management'

export const useFocusFilters = () => {
  const isMinScreenMd = isMinScreen('md', { shouldPassInSSR: true })
  const { isVisible: isFilterVisible } = useFilterSidebarVisibility()

  const focusFilterSidebar = (event?: KeyboardEvent, focus = Focus.Last) => {
    if (isMinScreenMd.value && isFilterVisible.value) {
      if (event) event.preventDefault()
      // Prevent over-tabbing to the element after the target one
      // Cannot use refs when using portals (for sidebar)
      const filtersSidebarElement = document.getElementById('filters')
      if (filtersSidebarElement) {
        focusIn(filtersSidebarElement, focus)
      }
    }
  }
  const focusFilterButton = (event?: KeyboardEvent) => {
    if (isMinScreenMd.value && isFilterVisible.value) {
      if (event) event.preventDefault()
      const filterButton = document.getElementById('filter-button')
      if (filterButton) {
        filterButton.focus()
      }
    }
  }

  return { focusFilterSidebar, focusFilterButton }
}
