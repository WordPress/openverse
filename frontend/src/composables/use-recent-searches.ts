import { computed, nextTick, ref, type Ref, watch } from "vue"

import { keycodes } from "~/constants/key-codes"
import { useSearchStore } from "~/stores/search"

import { cyclicShift } from "~/utils/math"

type VerticalArrow = typeof keycodes.ArrowUp | typeof keycodes.ArrowDown
type VerticalArrowEvent = KeyboardEvent & { key: VerticalArrow }
export const isVerticalArrowEvent = (
  event: KeyboardEvent
): event is VerticalArrowEvent => {
  return event.key === keycodes.ArrowUp || event.key === keycodes.ArrowDown
}

export const updateIndexOnVerticalArrow = (
  key: VerticalArrow,
  entriesCount: number,
  selectedIdx: number | undefined
) => {
  const defaultValue = key === keycodes.ArrowUp ? 0 : -1
  const offset = key === keycodes.ArrowUp ? -1 : 1
  return cyclicShift(selectedIdx ?? defaultValue, offset, 0, entriesCount)
}

export const useRecentSearches = ({
  focusInput,
  term,
  isMobile,
  isInputFocused,
}: {
  focusInput: () => void
  term: Ref<string>
  isMobile: boolean
  isInputFocused?: Ref<boolean> | undefined
}) => {
  const searchStore = useSearchStore()
  const isRecentVisible = ref(false)
  /**
   * Refers to the current suggestion that has visual focus (not DOM focus)
   * and is the active descendant. This should be set to `undefined` when the
   * visual focus is on the input field.
   */
  const selectedIdx = ref<number | undefined>(undefined)
  const entries = computed(() => searchStore.recentSearches)

  /**
   * Revert the search term to the existing value if the entered value is blank.
   */
  const hideRecentSearches = () => {
    isRecentVisible.value = false
    if (term.value === "" && searchStore.searchTerm !== "") {
      term.value = searchStore.searchTerm
    }
  }

  /**
   * Focus the search bar when opening the modal.
   * `nextTick` is necessary to ensure focus in Firefox
   */
  const showRecentSearches = () => {
    isRecentVisible.value = true
    nextTick(() => focusInput())
  }

  const recent = {
    isVisible: isRecentVisible,
    hide: hideRecentSearches,
    show: showRecentSearches,
    selectedIdx,
    entries,
  }

  const handleVerticalArrows = (event: VerticalArrowEvent) => {
    event.preventDefault() // Prevent the cursor from moving horizontally.
    const { key, altKey } = event
    showRecentSearches()
    if (altKey) {
      return
    }
    // Shift selection (if Alt was not pressed with arrow keys)
    selectedIdx.value = updateIndexOnVerticalArrow(
      key,
      entries.value.length,
      selectedIdx.value
    )
  }

  const shouldHideOnEvent = (event: KeyboardEvent, isMobile: boolean) => {
    // Always hide when the user presses Escape.
    if (event.key === keycodes.Escape) {
      return true
    }
    // Hide the recent searches popover when the user presses Enter or Shift+Tab on the input.
    return (
      !isMobile &&
      (event.key === keycodes.Enter ||
        (event.key === keycodes.Tab && event.shiftKey))
    )
  }

  const handleOtherKeys = (event: KeyboardEvent) => {
    const { key } = event
    if (key === keycodes.Enter && selectedIdx.value) {
      // If a recent search is selected, populate its value into the input.
      term.value = entries.value[selectedIdx.value]
    }
    if (shouldHideOnEvent(event, isMobile)) {
      hideRecentSearches()
    }
    if (
      isMobile &&
      !isRecentVisible.value &&
      isVerticalArrowEvent(event) &&
      isInputFocused
    ) {
      isInputFocused.value = false
    }
    selectedIdx.value = undefined // Lose visual focus from entries.
  }

  const handleKeydown = (event: KeyboardEvent) => {
    return isVerticalArrowEvent(event)
      ? handleVerticalArrows(event)
      : handleOtherKeys(event)
  }

  /**
   * Populate the input with the clicked entry and execute the search.
   */
  const handleSelect = (idx: number) => {
    term.value = entries.value[idx]
    hideRecentSearches()
    selectedIdx.value = undefined // Lose visual focus from entries.
  }

  /**
   * Clear recent searches from the store. Removes a single entry
   * if entry is provided, otherwise removes all recent searches.
   */
  const handleClear = (entry?: string) => {
    focusInput()
    useSearchStore().clearRecentSearches(entry)
  }

  watch(selectedIdx, (idx) => {
    if (idx !== undefined) {
      term.value = entries.value[idx]
    }
  })

  return {
    handleKeydown,
    handleSelect,
    handleClear,
    recent,
    isRecentVisible,
  }
}
