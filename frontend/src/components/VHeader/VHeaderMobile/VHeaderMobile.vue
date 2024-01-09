<template>
  <header
    ref="headerRef"
    class="main-header z-30 flex w-full items-center bg-white px-6 py-4"
  >
    <VInputModal
      class="flex w-full"
      variant="recent-searches"
      :is-active="isRecentSearchesModalOpen"
      aria-label="inputmodal"
      @close="deactivate"
    >
      <div class="flex w-full" :class="{ 'px-2': isRecentSearchesModalOpen }">
        <!-- Form action is a fallback for when JavaScript is disabled. -->
        <form
          action="/search"
          class="search-bar group flex h-12 w-full flex-row items-center overflow-hidden rounded-sm"
          :class="
            searchBarIsActive
              ? 'bg-white ring ring-pink'
              : 'bg-dark-charcoal-06'
          "
          @submit.prevent="handleSearch"
        >
          <slot name="start">
            <VLogoButton
              v-show="!searchBarIsActive"
              :is-fetching="isFetching"
            />
            <VSearchBarButton
              v-show="searchBarIsActive"
              icon="chevron-back"
              :label="$t('header.backButton')"
              :rtl-flip="true"
              variant="filled-gray"
              @click="handleBack"
            />
          </slot>

          <input
            id="search-bar"
            ref="searchInputRef"
            name="q"
            :placeholder="$t('hero.search.placeholder')"
            type="search"
            class="search-field ms-1 h-full w-full flex-grow appearance-none rounded-none border-tx bg-tx text-2xl text-dark-charcoal-70 placeholder-dark-charcoal-70 hover:text-dark-charcoal hover:placeholder-dark-charcoal focus-visible:outline-none"
            :value="searchTerm"
            :aria-label="
              $t('search.searchBarLabel', {
                openverse: 'Openverse',
              })
            "
            autocomplete="off"
            role="combobox"
            aria-autocomplete="none"
            :aria-expanded="showRecentSearches"
            aria-controls="recent-searches-list"
            :aria-activedescendant="
              selectedIdx !== undefined ? `option-${selectedIdx}` : undefined
            "
            @input="updateSearchText"
            @focus="activate"
            @keydown="handleKeydown"
          />
          <slot>
            <VSearchBarButton
              v-show="searchBarIsActive && searchTerm"
              icon="close-small"
              :label="$t('browsePage.searchForm.clear')"
              inner-area-classes="bg-white hover:bg-dark-charcoal-10"
              @click="clearSearchText"
            />
            <span
              v-show="!searchBarIsActive && searchStatus"
              class="info mx-4 hidden whitespace-nowrap text-xs group-hover:text-dark-charcoal group-focus:text-dark-charcoal md:flex"
            >
              {{ searchStatus }}
            </span>
            <VContentSettingsButton
              v-show="!searchBarIsActive"
              :is-pressed="contentSettingsOpen"
              :applied-filter-count="appliedFilterCount"
              v-bind="triggerA11yProps"
              :disabled="!doneHydrating"
              @click="toggleContentSettings"
            />
            <VContentSettingsModalContent
              variant="two-thirds"
              :visible="contentSettingsOpen"
              :is-fetching="isFetching"
              :close="closeContentSettings"
              labelledby="content-settings-button"
            />
          </slot>
        </form>
      </div>
      <ClientOnly>
        <VRecentSearches
          v-show="showRecentSearches"
          :selected-idx="selectedIdx"
          :entries="entries"
          :bordered="false"
          class="mt-4"
          @select="handleSelect"
          @clear="handleClear"
        />
      </ClientOnly>
    </VInputModal>
  </header>
</template>

<script lang="ts">
import { computed, defineComponent, nextTick, ref, watch } from "vue"

import { ensureFocus } from "~/utils/reakit-utils/focus"
import { cyclicShift } from "~/utils/math"

import { keycodes } from "~/constants/key-codes"

import { useAnalytics } from "~/composables/use-analytics"
import { useDialogControl } from "~/composables/use-dialog-control"
import { useSearch } from "~/composables/use-search"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"

import { useHydrating } from "~/composables/use-hydrating"

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

    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()

    const searchBarIsActive = ref(false)
    const contentSettingsOpen = ref(false)

    const isFetching = computed(() => mediaStore.fetchState.isFetching)

    const { sendCustomEvent } = useAnalytics()

    const { updateSearchState, searchTerm, searchStatus } =
      useSearch(sendCustomEvent)

    const handleSearch = async () => {
      window.scrollTo({ top: 0, left: 0, behavior: "auto" })
      updateSearchState()
      deactivate()
    }

    const isRecentSearchesModalOpen = ref(false)

    const activate = () => (searchBarIsActive.value = true)
    const deactivate = () => {
      searchBarIsActive.value = false
    }

    watch(searchBarIsActive, (active) => {
      if (active) {
        isRecentSearchesModalOpen.value = true
        /**
         * Without `nextTick`, the search bar is not focused on click in Firefox
         */
        nextTick(() => {
          if (searchInputRef.value) {
            ensureFocus(searchInputRef.value)
          }
        })
      } else {
        isRecentSearchesModalOpen.value = false
        if (searchTerm.value === "" && searchStore.searchTerm !== "") {
          searchTerm.value = searchStore.searchTerm
        }
      }
    })
    const appliedFilterCount = computed(() => searchStore.appliedFilterCount)

    const updateSearchText = (event: Event) => {
      searchTerm.value = (event.target as HTMLInputElement).value
    }

    const clearSearchText = () => {
      searchTerm.value = ""
      if (searchInputRef.value) {
        ensureFocus(searchInputRef.value)
      }
    }

    const handleBack = () => {
      deactivate()
    }

    /**
     * Refers to the current suggestion that has visual focus (not DOM focus)
     * and is the active descendant. This should be set to `undefined` when the
     * visual focus is on the input field.
     */
    const selectedIdx = ref<number | undefined>(undefined)
    const entries = computed(() => searchStore.recentSearches)
    const handleVerticalArrows = (event: KeyboardEvent) => {
      event.preventDefault() // Prevent the cursor from moving horizontally.
      const { key, altKey } = event
      // Show the recent searches.
      isRecentSearchesModalOpen.value = true
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
        isRecentSearchesModalOpen.value = false
      }
      selectedIdx.value = undefined // Lose visual focus from entries.
    }
    const handleKeydown = (event: KeyboardEvent) => {
      const { key } = event
      return ([keycodes.ArrowUp, keycodes.ArrowDown] as string[]).includes(key)
        ? handleVerticalArrows(event)
        : handleOtherKeys(event)
    }
    /* Populate the input with the clicked entry and execute the search. */
    const handleSelect = (idx: number) => {
      searchTerm.value = entries.value[idx]
      isRecentSearchesModalOpen.value = false
      selectedIdx.value = undefined // Lose visual focus from entries.
      handleSearch() // Immediately execute the search manually.
    }
    /* Clear all recent searches from the store. */
    const handleClear = () => {
      searchStore.clearRecentSearches()
      if (searchInputRef.value) {
        ensureFocus(searchInputRef.value)
      }
    }

    const showRecentSearches = computed(
      () => isRecentSearchesModalOpen.value && entries.value.length > 0
    )

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
      searchInputRef,
      headerRef,

      isFetching,

      appliedFilterCount,

      doneHydrating,
      contentSettingsOpen,
      openContentSettings,
      closeContentSettings,
      toggleContentSettings,
      triggerA11yProps,

      isRecentSearchesModalOpen,
      showRecentSearches,
      searchBarIsActive,
      activate,
      deactivate,

      searchStatus,
      searchTerm,
      clearSearchText,
      updateSearchText,
      handleSearch,

      handleBack,
      selectedIdx,
      entries,
      handleKeydown,
      handleSelect,
      handleClear,
    }
  },
})
</script>
