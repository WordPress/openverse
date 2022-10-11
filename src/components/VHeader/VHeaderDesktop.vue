<template>
  <header
    class="main-header z-30 flex w-full items-stretch justify-between gap-x-2 border-b bg-white py-4 px-7"
    :class="
      isHeaderScrolled || sidebarVisibleRef
        ? 'border-dark-charcoal-20'
        : 'border-white'
    "
  >
    <VLogoButton :is-fetching="isFetching" />

    <VSearchBar
      ref="searchBarRef"
      v-model.trim="searchTerm"
      class="flex-grow me-4"
      size="medium"
      @submit="handleSearch"
    >
      <VClearButton
        v-show="searchTerm !== ''"
        class="hidden me-2 group-focus-within:flex"
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
      :pressed="sidebarVisibleRef"
      :disabled="areFiltersDisabled"
      aria-haspopup="dialog"
      :aria-expanded="sidebarVisibleRef"
      @toggle="toggleSidebar"
      @tab="onTab"
    />
    <VTeleport v-if="sidebarVisibleRef" to="sidebar">
      <VSearchGridFilter @close="toggleSidebar" />
    </VTeleport>
  </header>
</template>
<script lang="ts">
import {
  computed,
  defineComponent,
  inject,
  onMounted,
  ref,
  useContext,
  useRouter,
  watch,
} from '@nuxtjs/composition-api'

import { Portal as VTeleport } from 'portal-vue'

import { useMediaStore } from '~/stores/media'
import { isSearchTypeSupported, useSearchStore } from '~/stores/search'

import { ALL_MEDIA, searchPath, supportedMediaTypes } from '~/constants/media'
import { IsHeaderScrolledKey } from '~/types/provides'
import { useI18n } from '~/composables/use-i18n'
import { useI18nResultsCount } from '~/composables/use-i18n-utilities'

import useSearchType from '~/composables/use-search-type'
import { useFilterSidebarVisibility } from '~/composables/use-filter-sidebar-visibility'
import { useFocusFilters } from '~/composables/use-focus-filters'

import local from '~/utils/local'
import { env } from '~/utils/env'
import { Focus } from '~/utils/focus-management'

import { ensureFocus } from '~/utils/reakit-utils/focus'

import VClearButton from '~/components/VHeader/VSearchBar/VClearButton.vue'
import VFilterButton from '~/components/VHeader/VFilterButton.vue'
import VSearchBar from '~/components/VHeader/VSearchBar/VSearchBar.vue'
import VLogoButton from '~/components/VHeader/VLogoButton.vue'
import VSearchGridFilter from '~/components/VFilters/VSearchGridFilter.vue'
import VSearchTypePopover from '~/components/VContentSwitcher/VSearchTypePopover.vue'

/**
 * The desktop search header.
 */
export default defineComponent({
  name: 'VHeaderDesktop',
  components: {
    VClearButton,
    VFilterButton,
    VLogoButton,
    VSearchGridFilter,
    VSearchTypePopover,
    VSearchBar,
    VTeleport,
  },
  setup(_, { emit }) {
    const filterButtonRef = ref<InstanceType<typeof VFilterButton> | null>(null)
    const searchBarRef = ref<InstanceType<typeof VSearchBar> | null>(null)

    const sidebarVisibleRef = ref(false)

    const { app } = useContext()
    const i18n = useI18n()
    const router = useRouter()

    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()

    const content = useSearchType()
    const filterSidebar = useFilterSidebarVisibility()

    const isHeaderScrolled = inject(IsHeaderScrolledKey)

    const isFetching = computed(() => mediaStore.fetchState.isFetching)

    const resultsCount = computed(() => mediaStore.resultCount)
    const { getI18nCount } = useI18nResultsCount()
    /**
     * Additional text at the end of the search bar.
     * Shows the loading state or result count.
     */
    const searchStatus = computed(() => {
      if (searchStore.searchTerm === '') return ''
      if (isFetching.value) return i18n.t('header.loading')
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
      searchTerm.value = ''
      ensureFocus(searchBarRef.value?.$el.querySelector('input') as HTMLElement)
    }

    const selectSearchType = async (type) => {
      content.setActiveType(type)

      const newPath = app.localePath({
        path: searchPath(type),
        query: searchStore.searchQueryParams,
      })
      router.push(newPath)

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
      window.scrollTo({ top: 0, left: 0, behavior: 'auto' })
      const mediaStore = useMediaStore()
      const searchStore = useSearchStore()
      const searchType = searchStore.searchType
      if (!searchTermChanged.value || searchTerm.value === '') return
      if (searchTermChanged.value) {
        await mediaStore.clearMedia()

        searchStore.setSearchTerm(searchTerm.value)
      }
      document.activeElement?.blur()
      if (isSearchTypeSupported(searchType)) {
        const newPath = app.localePath({
          path: searchPath(searchType),
          query: searchStore.searchQueryParams,
        })
        router.push(newPath)
      }
    }
    const areFiltersDisabled = computed(
      () => !searchStore.searchTypeIsSupported
    )

    onMounted(() => {
      // We default to show the filter on desktop, and only close it if the user has
      // explicitly closed it before.
      const localFilterState = !(
        local.getItem(env.filterStorageKey) === 'false'
      )
      const searchStore = useSearchStore()
      sidebarVisibleRef.value =
        searchStore.searchTypeIsSupported && localFilterState
    })

    watch(sidebarVisibleRef, (visible) => {
      filterSidebar.setVisibility(visible)
      visible ? emit('open') : emit('close')
    })

    const toggleSidebar = () =>
      (sidebarVisibleRef.value = !sidebarVisibleRef.value)

    const focusFilters = useFocusFilters()
    /**
     * Focus the first element in the sidebar when navigating from the VFilterButton
     * using keyboard `Tab` key.
     */
    const onTab = (event: KeyboardEvent) => {
      focusFilters.focusFilterSidebar(event, Focus.First)
    }

    return {
      filterButtonRef,
      searchBarRef,
      isFetching,

      isHeaderScrolled,
      areFiltersDisabled,

      close,

      handleSearch,
      clearSearchTerm,
      selectSearchType,
      searchStatus,
      searchTerm,
      sidebarVisibleRef,
      toggleSidebar,
      onTab,
    }
  },
})
</script>
