<template>
  <header
    class="main-header z-30 flex w-full items-center border-b border-tx bg-white px-6 py-4"
    :class="{ 'border-dark-charcoal-20': isHeaderScrolled }"
  >
    <VInputModal
      class="flex w-full"
      variant="recent-searches"
      :is-active="isRecentSearchesModalOpen"
      @close="deactivate"
    >
      <div class="flex w-full" :class="isRecentSearchesModalOpen ? 'px-2' : ''">
        <form
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
              :is-search-route="true"
              class="w-12"
            />
            <VSearchBarButton
              v-show="searchBarIsActive"
              :icon-path="chevronLeftIcon"
              :inner-size="8"
              :aria-label="$t('header.back-button')"
              :rtl-flip="true"
              inner-area-classes="bg-dark-charcoal-10 hover:bg-dark-charcoal hover:text-white"
              @click="handleBack"
            />
          </slot>

          <input
            id="search-bar"
            ref="searchInputRef"
            name="q"
            :placeholder="$t('hero.search.placeholder').toString()"
            type="search"
            class="search-field h-full w-full flex-grow appearance-none rounded-none border-tx bg-tx text-2xl text-dark-charcoal-70 placeholder-dark-charcoal-70 ms-1 hover:text-dark-charcoal hover:placeholder-dark-charcoal focus-visible:outline-none"
            :value="searchTerm"
            :aria-label="
              $t('search.search-bar-label', {
                openverse: 'Openverse',
              }).toString()
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
              :icon-path="closeIcon"
              :aria-label="$t('browse-page.search-form.clear')"
              inner-area-classes="bg-white hover:bg-dark-charcoal-10"
              @click="clearSearchText"
            />
            <span
              v-show="!searchBarIsActive && searchStatus"
              class="info mx-4 hidden whitespace-nowrap text-xs group-hover:text-dark-charcoal group-focus:text-dark-charcoal md:flex"
            >
              {{ searchStatus }}
            </span>
            <VContentSettingsModal
              v-show="!searchBarIsActive"
              :is-fetching="isFetching"
            />
          </slot>
        </form>
      </div>

      <VRecentSearches
        v-show="showRecentSearches"
        :selected-idx="selectedIdx"
        :entries="entries"
        :bordered="false"
        class="mt-4"
        @select="handleSelect"
        @clear="handleClear"
      />
    </VInputModal>
  </header>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  inject,
  nextTick,
  ref,
  useContext,
  useRouter,
  watch,
} from '@nuxtjs/composition-api'

import { ensureFocus } from '~/utils/reakit-utils/focus'
import { cyclicShift } from '~/utils/math'

import { searchPath } from '~/constants/media'
import { keycodes } from '~/constants/key-codes'

import { IsHeaderScrolledKey } from '~/types/provides'

import { useI18n } from '~/composables/use-i18n'
import { useI18nResultsCount } from '~/composables/use-i18n-utilities'

import { useMediaStore } from '~/stores/media'
import { isSearchTypeSupported, useSearchStore } from '~/stores/search'

import VLogoButton from '~/components/VHeader/VLogoButton.vue'
import VInputModal from '~/components/VModal/VInputModal.vue'
import VContentSettingsModal from '~/components/VHeader/VHeaderMobile/VContentSettingsModal.vue'
import VRecentSearches from '~/components/VRecentSearches/VRecentSearches.vue'
import VSearchBarButton from '~/components/VHeader/VHeaderMobile/VSearchBarButton.vue'

import closeIcon from '~/assets/icons/close-small.svg'
import chevronLeftIcon from '~/assets/icons/chevron-left.svg'

/**
 * Displays a text field for a search query and is attached to an action button
 * that fires a search request. The loading state and number of hits are also
 * displayed in the bar itself.
 */
export default defineComponent({
  name: 'VHeaderMobile',
  components: {
    VContentSettingsModal,
    VInputModal,
    VLogoButton,
    VRecentSearches,
    VSearchBarButton,
  },
  setup() {
    const searchInputRef = ref<HTMLInputElement | null>(null)

    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()
    const { app } = useContext()
    const i18n = useI18n()
    const router = useRouter()

    const searchBarIsActive = ref(false)

    const isHeaderScrolled = inject(IsHeaderScrolledKey)

    const isFetching = computed(() => mediaStore.fetchState.isFetching)

    const resultsCount = computed(() => mediaStore.resultCount)
    const { getI18nCount } = useI18nResultsCount()
    /**
     * Additional text at the end of the search bar.
     * Shows the loading state or result count.
     */
    const searchStatus = computed<string>(() => {
      if (searchStore.searchTerm === '') return ''
      if (isFetching.value) return i18n.t('header.loading').toString()
      return getI18nCount(resultsCount.value)
    })

    const localSearchTerm = ref(searchStore.searchTerm)
    let searchTermChanged = computed(() => {
      return searchStore.searchTerm !== localSearchTerm.value
    })
    /**
     * Search term has a getter and setter to be used as a v-model.
     * To prevent sending unnecessary requests, we also keep track of whether
     * the search term was changed.
     */
    const searchTerm = computed({
      get: () => localSearchTerm.value,
      set: (value: string) => {
        localSearchTerm.value = value
      },
    })

    /**
     * Called when the 'search' button in the header is clicked.
     * There are several scenarios:
     * - search term hasn't changed:
     *   - on a search route, do nothing.
     *   - on other routes: set searchType to 'All content', reset the media,
     *     change the path to `/search/` (All content).
     * - search term changed:
     *   - on a search route: Update the store searchTerm value, update query `q` param, reset media,
     *     fetch new media.
     *   - on other routes: Update the store searchTerm value, set searchType to 'All content', reset media,
     *     update query `q` param.
     * Updating the path causes the `search.vue` page's route watcher
     * to run and fetch new media.
     */
    const handleSearch = async () => {
      window.scrollTo({ top: 0, left: 0, behavior: 'auto' })
      const mediaStore = useMediaStore()
      const searchStore = useSearchStore()
      const searchType = searchStore.searchType
      if (!searchTermChanged.value || searchTerm.value === '') return
      if (searchTermChanged.value) {
        await mediaStore.clearMedia()

        searchStore.setSearchTerm(searchTerm.value)
        searchStore.setSearchType(searchType)
      }

      if (isSearchTypeSupported(searchType)) {
        const newPath = app.localePath({
          path: searchPath(searchType),
          query: searchStore.searchQueryParams,
        })
        router.push(newPath)
      }
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
          if (searchInputRef.value) ensureFocus(searchInputRef.value)
        })
      } else {
        isRecentSearchesModalOpen.value = false
        if (localSearchTerm.value === '' && searchStore.searchTerm !== '') {
          localSearchTerm.value = searchStore.searchTerm
        }
      }
    })

    const updateSearchText = (event: Event) => {
      searchTerm.value = (event.target as HTMLInputElement).value
    }

    const clearSearchText = () => {
      searchTerm.value = ''
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
      if (altKey) return
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
      if (key === keycodes.Enter && selectedIdx.value)
        // If a recent search is selected, populate its value into the input.
        searchTerm.value = entries.value[selectedIdx.value]
      if (([keycodes.Escape] as string[]).includes(key))
        // Hide the recent searches.
        isRecentSearchesModalOpen.value = false
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

    return {
      chevronLeftIcon: chevronLeftIcon as unknown as string,
      closeIcon: closeIcon as unknown as string,
      searchInputRef,

      isHeaderScrolled,
      isFetching,

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
