<template>
  <header
    ref="headerRef"
    class="main-header z-30 flex w-full items-center bg-white px-6 py-4"
  >
    <VInputModal
      class="flex w-full"
      variant="recent-searches"
      :is-active="isRecentSearchesModalOpen"
      :aria-label="$t('recentSearches.heading').toString()"
      @close="deactivate"
    >
      <div class="flex w-full" :class="{ 'px-3': isRecentSearchesModalOpen }">
        <!-- Form action is a fallback for when JavaScript is disabled. -->
        <form
          action="/search"
          class="search-bar group flex h-12 w-full flex-row items-center overflow-hidden rounded-sm"
          :class="
            searchBarIsActive || isInputFocused
              ? 'bg-white ring ring-pink'
              : 'bg-dark-charcoal-06'
          "
          @submit.prevent="handleSearch"
        >
          <slot name="start">
            <VLogoButton
              v-show="!isRecentSearchesModalOpen"
              :is-fetching="isFetching"
              class="focus-visible:me-1.5px focus-visible:ms-1.5px focus-visible:!h-[45px] focus-visible:max-w-[45px]"
            />
            <VSearchBarButton
              v-show="isRecentSearchesModalOpen"
              icon="chevron-back"
              :label="$t('header.backButton')"
              :rtl-flip="true"
              variant="filled-gray"
              @click="deactivate"
              @keydown.shift.tab="handleTabOut('backward')"
            />
          </slot>

          <input
            id="search-bar"
            ref="searchInputRef"
            name="q"
            :placeholder="$t('hero.search.placeholder').toString()"
            type="search"
            class="search-field ms-1 h-full w-full flex-grow appearance-none rounded-none border-tx bg-tx text-2xl text-dark-charcoal-70 placeholder-dark-charcoal-70 hover:text-dark-charcoal hover:placeholder-dark-charcoal focus-visible:outline-none"
            :value="searchTerm"
            :aria-label="
              $t('search.searchBarLabel', {
                openverse: 'Openverse',
              }).toString()
            "
            autocomplete="off"
            role="combobox"
            aria-autocomplete="none"
            :aria-expanded="isRecentSearchesModalOpen"
            aria-controls="recent-searches-list"
            :aria-activedescendant="
              selectedIdx !== undefined ? `option-${selectedIdx}` : undefined
            "
            @input="updateSearchText"
            @focus="handleInputFocus"
            @keydown="handleInputKeydown"
            @focusout="handleInputBlur"
            @click="handleInputClick"
          />
          <slot>
            <VSearchBarButton
              v-show="isRecentSearchesModalOpen && searchTerm"
              icon="close-small"
              :label="$t('browsePage.searchForm.clear')"
              inner-area-classes="bg-white hover:bg-dark-charcoal-10"
              @click="clearSearchText"
              @keydown.tab.exact="handleClearButtonTab"
            />
            <span
              v-show="!searchBarIsActive && searchStatus"
              class="info mx-4 hidden whitespace-nowrap text-xs group-hover:text-dark-charcoal group-focus:text-dark-charcoal md:flex"
            >
              {{ searchStatus }}
            </span>
            <VContentSettingsButton
              v-show="!searchBarIsActive"
              ref="contentSettingsButtonRef"
              :is-pressed="contentSettingsOpen"
              :applied-filter-count="appliedFilterCount"
              v-bind="triggerA11yProps"
              :disabled="!doneHydrating"
              @click="toggleContentSettings"
              @keydown.tab.exact="handleTabOut('forward')"
            />
            <VContentSettingsModalContent
              v-show="!isRecentSearchesModalOpen"
              variant="two-thirds"
              :visible="contentSettingsOpen"
              :is-fetching="isFetching"
              :close="closeContentSettings"
              :trigger-element="contentSettingsButton"
              labelledby="content-settings-button"
            />
          </slot>
        </form>
      </div>
      <ClientOnly>
        <VRecentSearches
          v-show="isRecentSearchesModalOpen"
          ref="recentSearchesRef"
          :selected-idx="selectedIdx"
          :entries="entries"
          :bordered="false"
          class="mt-4"
          @select="handleSelect"
          @clear="handleClear"
          @clear-single="handleClear($event)"
          @last-tab="handleTabOut('forward')"
        />
      </ClientOnly>
    </VInputModal>
  </header>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, ref } from "vue"
import { useContext } from "@nuxtjs/composition-api"
import { onClickOutside } from "@vueuse/core"

import {
  ensureFocus,
  getAllTabbableIn,
  getFirstTabbableIn,
} from "~/utils/reakit-utils/focus"
import { cyclicShift } from "~/utils/math"

import { keycodes } from "~/constants/key-codes"

import { useDialogControl } from "~/composables/use-dialog-control"
import { useSearch } from "~/composables/use-search"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"

import { useHydrating } from "~/composables/use-hydrating"

import { skipToContentTargetId } from "~/constants/window"

import VLogoButton from "~/components/VHeader/VLogoButton.vue"
import VInputModal from "~/components/VModal/VInputModal.vue"
import VContentSettingsModalContent from "~/components/VHeader/VHeaderMobile/VContentSettingsModalContent.vue"
import VContentSettingsButton from "~/components/VHeader/VHeaderMobile/VContentSettingsButton.vue"
import VRecentSearches from "~/components/VRecentSearches/VRecentSearches.vue"
import VSearchBarButton from "~/components/VHeader/VHeaderMobile/VSearchBarButton.vue"

/**
 * Displays a text field for a search query and is attached to an action button
 * that fires a search request. The loading state and number of hits are also
 * displayed in the bar itself.
 */
export default defineComponent({
  name: "VHeaderMobile",
  components: {
    VContentSettingsModalContent,
    VContentSettingsButton,
    VInputModal,
    VLogoButton,
    VRecentSearches,
    VSearchBarButton,
  },
  setup(_, { emit }) {
    const searchInputRef = ref<HTMLInputElement | null>(null)
    const headerRef = ref<HTMLElement | null>(null)
    const recentSearchesRef = ref<InstanceType<typeof VRecentSearches> | null>(
      null
    )
    const contentSettingsButtonRef = ref<InstanceType<
      typeof VContentSettingsButton
    > | null>(null)
    const contentSettingsButton = computed(
      () => (contentSettingsButtonRef.value?.$el as HTMLElement) ?? undefined
    )

    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()

    const searchBarIsActive = ref(false)
    const isRecentSearchesModalOpen = ref(false)
    const isInputFocused = ref(false)
    const contentSettingsOpen = ref(false)

    const appliedFilterCount = computed(() => searchStore.appliedFilterCount)
    const isFetching = computed(() => mediaStore.fetchState.isFetching)

    /**
     * The selection range of the input field. Used to make sure that the cursor
     * is at the correct position when the search bar is clicked on.
     */
    const selection = ref<{ start: number; end: number }>({ start: 0, end: 0 })

    const entries = computed(() => searchStore.recentSearchEntries)

    const { $sendCustomEvent } = useContext()
    const { updateSearchState, searchTerm, searchStatus } =
      useSearch($sendCustomEvent)

    const focusInput = () => {
      const input = searchInputRef.value as HTMLInputElement
      ensureFocus(input)
      input.selectionStart = selection.value.start
      input.selectionEnd = selection.value.end
    }

    const handleSearch = async () => {
      window.scrollTo({ top: 0, left: 0, behavior: "auto" })
      updateSearchState()
      deactivate()
    }

    /**
     * Activate the search bar and open the recent searches modal.
     */
    const activate = () => {
      isInputFocused.value = true
      searchBarIsActive.value = true
      if (!isRecentSearchesModalOpen.value) {
        openRecentSearchesModal()
      }
    }

    /**
     * Deactivate the search bar and close the recent searches modal.
     */
    const deactivate = () => {
      isInputFocused.value = false
      searchBarIsActive.value = false
      closeRecentSearchesModal()
    }

    /**
     * Focus the search bar when opening the modal.
     * `nextTick` is necessary to ensure focus in Firefox
     */
    const openRecentSearchesModal = () => {
      isRecentSearchesModalOpen.value = true
      nextTick(() => focusInput())
    }

    /**
     * Revert the search term to the existing value if the entered value is blank.
     */
    const closeRecentSearchesModal = () => {
      isRecentSearchesModalOpen.value = false
      if (searchTerm.value === "" && searchStore.searchTerm !== "") {
        searchTerm.value = searchStore.searchTerm
      }
    }

    /**
     * Set the selection range of the input field to the saved value.
     * This is necessary because when opening the recent search modal,
     * the input field is blurred and focused again.
     */
    const updateSelection = (inputElement: HTMLInputElement) => {
      const lastPos =
        inputElement.value.length > 0 ? inputElement.value.length - 1 : 0
      selection.value = {
        start: inputElement.selectionStart ?? lastPos,
        end: inputElement.selectionEnd ?? lastPos,
      }
    }

    /**
     * When the user tabs into the input field, the `isInputFocused` is set to true,
     * but the search bar is not activated until the user types something.
     *
     * On the `input` event, update the search term and the selection range,
     * and activate the search bar.
     */
    const updateSearchText = (event: Event) => {
      const inputElement = event.target as HTMLInputElement
      searchTerm.value = inputElement.value
      updateSelection(inputElement)
      if (isInputFocused.value && !searchBarIsActive.value) {
        activate()
      }
    }

    const clearSearchText = () => {
      searchTerm.value = ""
      focusInput()
    }

    /**
     * Refers to the current suggestion that has visual focus (not DOM focus)
     * and is the active descendant. This should be set to `undefined` when the
     * visual focus is on the input field.
     */
    const selectedIdx = ref<number | undefined>(undefined)
    const handleVerticalArrows = (event: KeyboardEvent) => {
      event.preventDefault() // Prevent the cursor from moving horizontally.
      const { key, altKey } = event
      // Show the recent searches.
      openRecentSearchesModal()
      if (altKey) {
        return
      }
      // Shift selection (if Alt was not pressed with arrow keys)
      let defaultValue: number
      let offset: number
      if (key == keycodes.ArrowUp) {
        defaultValue = 0
        offset = -1
      } else {
        defaultValue = -1
        offset = 1
      }
      selectedIdx.value = cyclicShift(
        selectedIdx.value ?? defaultValue,
        offset,
        0,
        entries.value.length
      )
    }
    const handleOtherKeys = (event: KeyboardEvent) => {
      const { key } = event
      if (key === keycodes.Enter && selectedIdx.value) {
        // If a recent search is selected, populate its value into the input.
        searchTerm.value = entries.value[selectedIdx.value]
      }
      if (([keycodes.Escape] as string[]).includes(key)) {
        // Hide the recent searches.
        closeRecentSearchesModal()
      }
      if (key === keycodes.Tab) {
        // Keep `focused` as true when the user tabs out of the input.
        isInputFocused.value = false
      }
      if (
        !isRecentSearchesModalOpen.value &&
        (key === keycodes.ArrowRight || key === keycodes.ArrowLeft)
      ) {
        // Open recent searches when the user navigates horizontally.
        openRecentSearchesModal()
      }

      selectedIdx.value = undefined // Lose visual focus from entries.
    }

    const handleInputKeydown = (event: KeyboardEvent) => {
      const { key } = event
      return ([keycodes.ArrowUp, keycodes.ArrowDown] as string[]).includes(key)
        ? handleVerticalArrows(event)
        : handleOtherKeys(event)
    }
    /* Populate the input with the clicked entry and execute the search. */
    const handleSelect = (idx: number) => {
      searchTerm.value = entries.value[idx]
      closeRecentSearchesModal()
      selectedIdx.value = undefined // Lose visual focus from entries.
      handleSearch() // Immediately execute the search manually.
    }

    const handleInputFocus = () => (isInputFocused.value = true)
    const handleInputBlur = () => {
      if (!isRecentSearchesModalOpen.value && isInputFocused.value) {
        deactivate()
      }
    }

    /**
     * Deactivate the search bar when the user clicks outside the header,
     * but not when the click is inside the recent searches modal.
     */
    onClickOutside(headerRef, (event) => {
      const clickInsideModal = recentSearchesRef.value?.$el?.contains(
        event.target as Node
      )
      if (!clickInsideModal) {
        isInputFocused.value = false
      }
    })

    /**
     * When activating the search bar by clicking, preserve the cursor position.
     */
    const handleInputClick = (event: Event) => {
      if (!searchBarIsActive.value) {
        updateSelection(event.target as HTMLInputElement)
        activate()
      }
    }

    /**
     * Clear recent searches from the store. Removes a single entry
     * if entry is provided, otherwise removes all recent searches.
     */
    const handleClear = (entry?: string) => {
      searchStore.clearRecentSearches(entry)
      focusInput()
    }

    /**
     * Close the modal when the last clickable element is clicked
     * (clear button when there are no recent searches).
     */
    const handleClearButtonTab = () => {
      if (!entries.value.length) {
        handleTabOut("forward")
      }
    }

    /**
     * Special handling of focus order after leaving the search bar because
     * the input modal is inserted into the page and change the HTML elements order.
     * @param direction
     */
    const handleTabOut = (direction: "forward" | "backward") => {
      deactivate()
      nextTick().then(() => {
        let element =
          direction === "forward"
            ? document.getElementById(skipToContentTargetId)
            : getAllTabbableIn(document.body)[1]
        if (!element) {
          element = getFirstTabbableIn(document.body)
        }
        ensureFocus(element as HTMLElement)
      })
    }

    const {
      close: closeContentSettings,
      open: openContentSettings,
      onTriggerClick: toggleContentSettings,
      triggerA11yProps,
    } = useDialogControl({
      visibleRef: contentSettingsOpen,
      nodeRef: headerRef,
      lockBodyScroll: true,
      emit,
    })

    const { doneHydrating } = useHydrating()

    return {
      isInputFocused,
      searchInputRef,
      headerRef,
      recentSearchesRef,
      contentSettingsButtonRef,
      contentSettingsButton,

      isFetching,
      appliedFilterCount,
      doneHydrating,

      contentSettingsOpen,
      triggerA11yProps,
      openContentSettings,
      closeContentSettings,
      toggleContentSettings,

      searchStatus,
      searchTerm,
      searchBarIsActive,
      deactivate,
      handleInputFocus,
      handleInputBlur,
      handleInputClick,
      handleInputKeydown,

      clearSearchText,
      updateSearchText,
      handleSearch,

      isRecentSearchesModalOpen,
      selectedIdx,
      entries,
      handleSelect,
      handleClear,
      handleClearButtonTab,
      handleTabOut,
    }
  },
})
</script>
