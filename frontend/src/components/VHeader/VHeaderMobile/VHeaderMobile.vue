<template>
  <header
    ref="headerRef"
    class="main-header z-30 flex w-full items-center px-6 py-4"
  >
    <!-- Form action is a fallback for when JavaScript is disabled. -->
    <form
      action="/search"
      class="search-bar group flex h-12 w-full flex-row items-center overflow-hidden rounded-sm"
      :class="
        isSearchBarActive || isInputFocused
          ? 'ring-pink-8 bg-bg ring'
          : 'bg-bg-surface'
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
        class="search-field hover:text-text hover:placeholder-gray-12 text-text-secondary placeholder-gray-8 ms-1 h-full w-full flex-grow appearance-none rounded-none border-tx bg-tx text-2xl focus-visible:outline-none"
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
        aria-controls="recent-searches-list"
        aria-haspopup="listbox"
        :aria-activedescendant="
          selectedIdx === undefined ? undefined : `option-${selectedIdx}`
        "
        @input="updateSearchText"
        @keydown="handleInputKeydown"
        @focus="handleInputFocus"
        @focusout="handleInputBlur"
        @click="handleInputClick"
      />
      <VSearchBarButton
        v-show="isRecentVisible && localSearchTerm"
        ref="clearButtonRef"
        icon="close-small"
        :label="$t('browsePage.searchForm.clear')"
        inner-area-classes="bg-bg hover:bg-bg-fill-secondary"
        @click="clearSearchText"
        @keydown.tab.exact="handleTab($event, 'clear-input')"
      />
      <span
        v-show="!isSearchBarActive && searchStatus"
        class="info group-hover:text-text group-focus:text-text mx-4 hidden whitespace-nowrap text-xs md:flex"
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
        @keydown.tab.exact="handleTab($event, 'content-settings')"
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
    </form>
    <VModalContent
      v-if="isRecentVisible"
      :visible="true"
      :hide="deactivate"
      :trigger-element="searchInputRef"
      :trap-focus="false"
      :auto-focus-on-show="false"
      :auto-focus-on-hide="false"
      content-classes="px-3"
      :aria-label="$t('recentSearches.heading')"
      variant="mobile-input"
    >
      <ClientOnly>
        <VRecentSearches
          ref="recentSearchesRef"
          class="w-[100dvw] px-3"
          :selected-idx="selectedIdx"
          :entries="entries"
          :bordered="false"
          @select="handleSelect"
          @clear="handleClear"
          @last-tab="handleTabOut('forward')"
        />
      </ClientOnly>
    </VModalContent>
  </header>
</template>

<script lang="ts">
import { firstParam, focusIn, useNuxtApp, useRoute, useRouter } from "#imports"

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
    const clearButtonRef = ref<InstanceType<typeof VSearchBarButton> | null>(
      null
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
        const element =
          direction === "forward"
            ? document.getElementById(skipToContentTargetId)
            : getAllTabbableIn(document.body)[1]
        ensureFocus(
          element ?? (getFirstTabbableIn(document.body) as HTMLElement)
        )
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

    const router = useRouter()
    router.beforeEach((to, from, next) => {
      if (to.path !== from.path) {
        closeContentSettings()
        deactivate()
      }
      next()
    })

    const handleTab = (
      event: KeyboardEvent & { key: "Tab" },
      button: "content-settings" | "clear-input"
    ) => {
      if (recent.isVisible.value) {
        event.preventDefault()
        focusIn(recentSearchesRef.value?.$el, 1)
      } else if (button === "content-settings") {
        handleTabOut("forward")
      }
    }

    return {
      isInputFocused,
      searchInputRef,
      headerRef,
      recentSearchesRef,
      clearButtonRef,
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
      handleTab,
    }
  },
})
</script>
