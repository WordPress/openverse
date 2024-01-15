<template>
  <header
    ref="headerRef"
    class="main-header z-30 flex w-full items-center bg-white px-6 py-4"
  >
    <VInputModal
      class="flex w-full"
      :is-active="isRecentVisible"
      :aria-label="$t('recentSearches.heading')"
      @close="hideRecentSearches"
    >
      <div class="flex w-full" :class="{ 'px-3': isRecentVisible }">
        <!-- Form action is a fallback for when JavaScript is disabled. -->
        <form
          action="/search"
          class="search-bar group flex h-12 w-full flex-row items-center overflow-hidden rounded-sm"
          :class="
            isSearchBarActive || isInputFocused
              ? 'bg-white ring ring-pink'
              : 'bg-dark-charcoal-06'
          "
          @submit.prevent="handleFormSubmit"
        >
          <slot name="start">
            <VLogoButton
              v-show="!isRecentVisible"
              :is-fetching="isFetching"
              class="focus-visible:me-1.5px focus-visible:ms-1.5px focus-visible:!h-[45px] focus-visible:max-w-[45px]"
            />
            <VSearchBarButton
              v-show="isRecentVisible"
              icon="chevron-back"
              :label="$t('header.backButton')"
              :rtl-flip="true"
              variant="filled-gray"
              @click="hideRecentSearches"
              @keydown.shift.tab="handleTabOut('backward')"
            />
          </slot>

          <input
            id="search-bar"
            ref="searchInputRef"
            name="q"
            :placeholder="$t('hero.search.placeholder')"
            type="search"
            class="search-field ms-1 h-full w-full flex-grow appearance-none rounded-none border-tx bg-tx text-2xl text-dark-charcoal-70 placeholder-dark-charcoal-70 hover:text-dark-charcoal hover:placeholder-dark-charcoal focus-visible:outline-none"
            :value="localSearchTerm"
            :aria-label="
              $t('search.searchBarLabel', {
                openverse: 'Openverse',
              })
            "
            autocomplete="off"
            role="combobox"
            aria-autocomplete="list"
            :aria-expanded="isRecentVisible ? 'true' : 'false'"
            aria-owns="recent-searches-list"
            aria-controls="recent-searches-list"
            :aria-activedescendant="
              selectedIdx === undefined ? undefined : `option-${selectedIdx}`
            "
            @input="updateSearchText"
            @keydown="handleInputKeydown"
            @focus="handleInputFocus"
            @focusout="handleInputBlur"
            @click="handleInputClick"
          />
          <slot>
            <VSearchBarButton
              v-show="isRecentVisible && localSearchTerm"
              icon="close-small"
              :label="$t('browsePage.searchForm.clear')"
              inner-area-classes="bg-white hover:bg-dark-charcoal-10"
              @click="clearSearchText"
              @keydown.tab.exact="handleClearButtonTab"
            />
            <span
              v-show="!isSearchBarActive && searchStatus"
              class="info mx-4 hidden whitespace-nowrap text-xs group-hover:text-dark-charcoal group-focus:text-dark-charcoal md:flex"
            >
              {{ searchStatus }}
            </span>
            <VContentSettingsButton
              v-show="!isRecentVisible"
              ref="contentSettingsButtonRef"
              :is-pressed="contentSettingsOpen"
              :applied-filter-count="appliedFilterCount"
              v-bind="triggerA11yProps"
              :disabled="!doneHydrating"
              @click="toggleContentSettings"
              @keydown.tab.exact="handleTabOut('forward')"
            />
            <VContentSettingsModalContent
              v-show="!isRecentVisible"
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
          v-show="isRecentVisible"
          ref="recentSearchesRef"
          :selected-idx="selectedIdx"
          :entries="entries"
          :bordered="false"
          class="mt-4"
          @select="handleSelect"
          @clear="handleClear"
          @last-tab="handleTabOut('forward')"
        />
      </ClientOnly>
    </VInputModal>
  </header>
</template>

<script lang="ts">
import { firstParam, useNuxtApp, useRoute } from "#imports"

import { computed, defineComponent, nextTick, ref, watch } from "vue"
import { onClickOutside } from "@vueuse/core"

import {
  ensureFocus,
  getAllTabbableIn,
  getFirstTabbableIn,
} from "~/utils/reakit-utils/focus"

import { useDialogControl } from "~/composables/use-dialog-control"
import { useSearch } from "~/composables/use-search"
import { useHydrating } from "~/composables/use-hydrating"
import { useRecentSearches } from "~/composables/use-recent-searches"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"

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

    const isSearchBarActive = ref(false)
    const isInputFocused = ref(false)
    const contentSettingsOpen = ref(false)

    const appliedFilterCount = computed(() => searchStore.appliedFilterCount)
    const isFetching = computed(() => mediaStore.fetchState.isFetching)

    /**
     * The selection range of the input field. Used to make sure that the cursor
     * is at the correct position when the search bar is clicked on.
     */
    const selection = ref<{ start: number; end: number }>({ start: 0, end: 0 })

    const { $sendCustomEvent } = useNuxtApp()
    const { updateSearchState, searchTerm, searchStatus } =
      useSearch($sendCustomEvent)
    const localSearchTerm = ref(searchTerm.value)

    const focusInput = () => {
      const input = searchInputRef.value as HTMLInputElement
      ensureFocus(input)
      input.selectionStart = selection.value.start
      input.selectionEnd = selection.value.end
    }

    const handleFormSubmit = () => {
      if (localSearchTerm.value && localSearchTerm.value !== searchTerm.value) {
        searchTerm.value = localSearchTerm.value
      }
      recent.hide()
      handleSearch()
    }
    const handleSearch = () => {
      window.scrollTo({ top: 0, left: 0, behavior: "auto" })
      updateSearchState()
    }

    /**
     * Activate the search bar and open the recent searches modal.
     */
    const activate = () => {
      isInputFocused.value = true
      isSearchBarActive.value = true
      if (!recent.isVisible.value) {
        recent.show()
      }
    }

    /** Deactivate the search bar */
    const deactivate = () => {
      isInputFocused.value = false
      isSearchBarActive.value = false
    }

    /**
     * Set the selection range of the input field to the saved value.
     * This is necessary because when opening the recent search modal,
     * the input field is blurred and focused again.
     */
    const updateSelection = () => {
      const inputElement = searchInputRef.value as HTMLInputElement
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
    const updateSearchText = () => {
      localSearchTerm.value = (searchInputRef.value as HTMLInputElement).value
      updateSelection()
      if (isInputFocused.value && !isSearchBarActive.value) {
        activate()
      }
    }

    const clearSearchText = () => {
      localSearchTerm.value = ""
      focusInput()
    }

    const {
      handleKeydown: handleInputKeydown,
      handleSelect,
      handleClear,
      recent,
    } = useRecentSearches({
      focusInput,
      term: localSearchTerm,
      isMobile: true,
      isInputFocused,
    })

    watch(recent.isVisible, (isVisible) => {
      if (!isVisible) {
        deactivate()
        if (localSearchTerm.value !== searchTerm.value) {
          searchTerm.value = localSearchTerm.value
          handleSearch()
        }
      }
    })

    const handleInputFocus = () => (isInputFocused.value = true)
    const handleInputBlur = () => {
      if (!recent.isVisible.value && isInputFocused.value) {
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
    const handleInputClick = () => {
      if (!isSearchBarActive.value) {
        updateSelection()
        activate()
      }
    }

    /**
     * Close the modal when the last clickable element is clicked
     * (clear button when there are no recent searches).
     */
    const handleClearButtonTab = () => {
      if (!recent.entries.value.length) {
        handleTabOut("forward")
      }
    }

    /**
     * Special handling of focus order after leaving the search bar because
     * the input modal is inserted into the page and change the HTML elements order.
     * @param direction
     */
    const handleTabOut = (direction: "forward" | "backward") => {
      recent.hide()
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
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      emit: emit as (event: string, ...args: any[]) => void,
    })

    const route = useRoute()
    const routeSearchTerm = computed(() => firstParam(route?.query.q))
    watch(routeSearchTerm, (newSearchTerm) => {
      localSearchTerm.value = newSearchTerm ?? ""
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
      localSearchTerm,
      isSearchBarActive,
      deactivate,
      handleInputFocus,
      handleInputBlur,
      handleInputClick,
      handleInputKeydown,

      clearSearchText,
      updateSearchText,
      handleSearch,
      handleFormSubmit,

      isRecentVisible: recent.isVisible,
      selectedIdx: recent.selectedIdx,
      entries: recent.entries,
      hideRecentSearches: recent.hide,
      handleSelect,
      handleClear,
      handleClearButtonTab,
      handleTabOut,
    }
  },
})
</script>
