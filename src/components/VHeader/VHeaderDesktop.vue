<template>
  <header
    class="main-header z-30 flex w-full items-stretch justify-between gap-x-2 border-b bg-white py-4 px-6"
    :class="
      isHeaderScrolled || isSidebarVisible
        ? 'border-dark-charcoal-20'
        : 'border-white'
    "
  >
    <VLogoButton :is-fetching="isFetching" class="h-12" />

    <VSearchBar
      ref="searchBarRef"
      v-model.trim="searchTerm"
      class="flex-grow me-4"
      size="medium"
      @submit="handleSearch"
    >
      <VSearchBarButton
        v-show="searchTerm !== ''"
        :icon-path="closeIcon"
        :aria-label="$t('browse-page.search-form.clear')"
        inner-area-classes="bg-white hover:bg-dark-charcoal-10"
        class="hidden group-focus-within:flex"
        @click="clearSearchTerm"
      />
      <span
        v-show="Boolean(searchStatus)"
        class="info mx-4 hidden whitespace-nowrap text-xs text-dark-charcoal-70 group-focus-within:hidden group-hover:text-dark-charcoal group-focus:text-dark-charcoal lg:block"
      >
        {{ searchStatus }}
      </span>
    </VSearchBar>

    <VSearchTypePopover />

    <VFilterButton
      ref="filterButtonRef"
      class="flex self-stretch"
      :pressed="isSidebarVisible"
      :disabled="areFiltersDisabled"
      aria-haspopup="dialog"
      :aria-expanded="isSidebarVisible"
      @toggle="toggleSidebar"
      @tab="onTab"
    />
  </header>
</template>
<script lang="ts">
import {
  computed,
  defineComponent,
  inject,
  ref,
  useRouter,
} from "@nuxtjs/composition-api"

import { useMediaStore } from "~/stores/media"
import { isSearchTypeSupported, useSearchStore } from "~/stores/search"
import { useUiStore } from "~/stores/ui"

import { ALL_MEDIA, supportedMediaTypes } from "~/constants/media"
import { IsHeaderScrolledKey, IsSidebarVisibleKey } from "~/types/provides"

import { useI18n } from "~/composables/use-i18n"
import { useI18nResultsCount } from "~/composables/use-i18n-utilities"
import { useFocusFilters } from "~/composables/use-focus-filters"
import useSearchType from "~/composables/use-search-type"

import { Focus } from "~/utils/focus-management"
import { ensureFocus } from "~/utils/reakit-utils/focus"

import VFilterButton from "~/components/VHeader/VFilterButton.vue"
import VSearchBar from "~/components/VHeader/VSearchBar/VSearchBar.vue"
import VLogoButton from "~/components/VHeader/VLogoButton.vue"
import VSearchBarButton from "~/components/VHeader/VHeaderMobile/VSearchBarButton.vue"
import VSearchTypePopover from "~/components/VContentSwitcher/VSearchTypePopover.vue"

import closeIcon from "~/assets/icons/close-small.svg"

/**
 * The desktop search header.
 */
export default defineComponent({
  name: "VHeaderDesktop",
  components: {
    VFilterButton,
    VLogoButton,
    VSearchBarButton,
    VSearchTypePopover,
    VSearchBar,
  },
  setup() {
    const filterButtonRef = ref<InstanceType<typeof VFilterButton> | null>(null)
    const searchBarRef = ref<InstanceType<typeof VSearchBar> | null>(null)

    const i18n = useI18n()
    const router = useRouter()

    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()
    const uiStore = useUiStore()

    const content = useSearchType()

    const isHeaderScrolled = inject(IsHeaderScrolledKey)
    const isSidebarVisible = inject(IsSidebarVisibleKey)

    const isFetching = computed(() => mediaStore.fetchState.isFetching)

    const resultsCount = computed(() => mediaStore.resultCount)
    const { getI18nCount } = useI18nResultsCount()
    /**
     * Additional text at the end of the search bar.
     * Shows the loading state or result count.
     */
    const searchStatus = computed(() => {
      if (searchStore.searchTerm === "") return ""
      if (isFetching.value) return i18n.t("header.loading")
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

    const clearSearchTerm = () => {
      searchTerm.value = ""
      ensureFocus(searchBarRef.value?.$el.querySelector("input") as HTMLElement)
    }

    const selectSearchType = async (type) => {
      content.setActiveType(type)

      router.push(searchStore.getSearchPath({ type }))

      function typeWithoutMedia(mediaType) {
        return mediaStore.resultCountsPerMediaType[mediaType] === 0
      }

      const shouldFetchMedia =
        type === ALL_MEDIA
          ? supportedMediaTypes.every((type) => typeWithoutMedia(type))
          : typeWithoutMedia(type)

      if (shouldFetchMedia) {
        await mediaStore.fetchMedia()
      }
    }

    /**
     * Called when the 'search' button in the header is clicked.
     * There are several scenarios:
     * - search term hasn't changed:
     *   - do nothing.
     * - search term changed:
     *   - Update the store searchTerm value, update query `q` param, reset media,
     *     fetch new media.
     * Updating the path causes the `search.vue` page's route watcher
     * to run and fetch new media.
     */
    const handleSearch = async () => {
      window.scrollTo({ top: 0, left: 0, behavior: "auto" })
      const mediaStore = useMediaStore()
      const searchStore = useSearchStore()
      const searchType = searchStore.searchType
      if (!searchTermChanged.value || searchTerm.value === "") return
      if (searchTermChanged.value) {
        await mediaStore.clearMedia()

        searchStore.setSearchTerm(searchTerm.value)
      }
      document.activeElement?.blur()
      if (isSearchTypeSupported(searchType)) {
        router.push(searchStore.getSearchPath({ type: searchType }))
      }
    }
    const areFiltersDisabled = computed(
      () => !searchStore.searchTypeIsSupported
    )

    const toggleSidebar = () => uiStore.toggleFilters()

    const focusFilters = useFocusFilters()
    /**
     * Focus the first element in the sidebar when navigating from the VFilterButton
     * using keyboard `Tab` key.
     */
    const onTab = (event: KeyboardEvent) => {
      focusFilters.focusFilterSidebar(event, Focus.First)
    }

    return {
      closeIcon,
      filterButtonRef,
      searchBarRef,
      isFetching,

      isHeaderScrolled,
      isSidebarVisible,
      areFiltersDisabled,

      handleSearch,
      clearSearchTerm,
      selectSearchType,
      searchStatus,
      searchTerm,
      toggleSidebar,
      onTab,
    }
  },
})
</script>
