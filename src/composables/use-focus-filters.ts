import { Focus, focusIn } from "~/utils/focus-management"
import { useUiStore } from "~/stores/ui"

export const useFocusFilters = () => {
  const focusFilterSidebar = (event?: KeyboardEvent, focus = Focus.Last) => {
    const uiStore = useUiStore()
    if (uiStore.isDesktopLayout && uiStore.isFilterVisible) {
      if (event) event.preventDefault()
      // Prevent over-tabbing to the element after the target one
      // Cannot use refs when using portals (for sidebar)
      const filtersSidebarElement = document.getElementById("filters")
      if (filtersSidebarElement) {
        focusIn(filtersSidebarElement, focus)
      }
    }
  }
  const focusFilterButton = (event?: KeyboardEvent) => {
    const uiStore = useUiStore()
    if (uiStore.isDesktopLayout && uiStore.isFilterVisible) {
      if (event) event.preventDefault()
      const filterButton = document.getElementById("filter-button")
      if (filterButton) {
        filterButton.focus()
      }
    }
  }

  return { focusFilterSidebar, focusFilterButton }
}
