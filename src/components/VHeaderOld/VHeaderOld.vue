<template>
  <header
    class="main-header z-30 flex w-full items-center justify-between gap-x-2 gap-y-4 bg-white px-4 py-3 md:items-stretch md:py-4 md:px-7"
    :class="{
      'flex-wrap md:flex-nowrap': !isHeaderScrolled,
      'border-b border-white': !isHeaderScrolled && !isMenuOpen,
      'border-b border-dark-charcoal-20':
        isSearchRoute && (isHeaderScrolled || isMenuOpen),
      'md:justify-start': !isSearchRoute,
      'flex-nowrap': !isSearchRoute && isHeaderScrolled,
    }"
  >
    <VLogoButtonOld
      :is-fetching="isFetching"
      :is-header-scrolled="isHeaderScrolled"
      :is-search-route="isSearchRoute"
      class="md:h-12"
    />

    <VSearchBarOld
      v-model.trim="searchTerm"
      class="flex-grow lg:w-1/2 lg:flex-grow-0 2xl:w-1/3"
      :size="isDesktopLayout ? 'medium' : isHeaderScrolled ? 'small' : 'large'"
      :class="{
        'order-4 w-full md:order-none md:w-auto': !isHeaderScrolled,
      }"
      @submit="handleSearch"
    >
      <span
        v-show="searchStatus"
        class="info mx-4 hidden whitespace-nowrap text-xs font-semibold text-dark-charcoal-70 group-hover:text-dark-charcoal group-focus:text-dark-charcoal lg:block"
      >
        {{ searchStatus }}
      </span>
    </VSearchBarOld>

    <VHeaderMenu
      :is-search-route="isSearchRoute"
      @open="openMenuModal(menus.CONTENT_SWITCHER)"
      @close="close"
    />
    <VHeaderFilter
      v-if="isSearchRoute"
      :disabled="areFiltersDisabled"
      @open="openMenuModal(menus.FILTERS)"
      @close="close"
    />
  </header>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  inject,
  ref,
  useContext,
  useRouter,
} from '@nuxtjs/composition-api'

import { ALL_MEDIA, searchPath } from '~/constants/media'
import { useMatchSearchRoutes } from '~/composables/use-match-routes'
import { useI18n } from '~/composables/use-i18n'
import { useI18nResultsCount } from '~/composables/use-i18n-utilities'

import { useMediaStore } from '~/stores/media'
import { isSearchTypeSupported, useSearchStore } from '~/stores/search'
import { useUiStore } from '~/stores/ui'

import { IsSidebarVisibleKey } from '~/types/provides'

import VLogoButtonOld from '~/components/VHeaderOld/VLogoButtonOld.vue'
import VHeaderFilter from '~/components/VHeaderOld/VHeaderFilter.vue'
import VSearchBarOld from '~/components/VHeaderOld/VSearchBar/VSearchBarOld.vue'
import VHeaderMenu from '~/components/VHeaderOld/VHeaderMenu.vue'

import closeIcon from '~/assets/icons/close.svg'

const menus = {
  FILTERS: 'filters',
  CONTENT_SWITCHER: 'content-switcher',
}
type HeaderMenu = 'filters' | 'content-switcher'

export default defineComponent({
  name: 'VHeaderOld',
  components: {
    VLogoButtonOld,
    VHeaderFilter,
    VHeaderMenu,
    VSearchBarOld,
  },
  setup() {
    const { app } = useContext()
    const i18n = useI18n()
    const router = useRouter()

    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()
    const uiStore = useUiStore()

    const { matches: isSearchRoute } = useMatchSearchRoutes()

    const isHeaderScrolled = inject('isHeaderScrolled', false)
    const headerHasTwoRows = inject('headerHasTwoRows')
    const isSidebarVisible = inject(IsSidebarVisibleKey)

    const isDesktopLayout = computed(() => uiStore.isDesktopLayout)

    const openMenu = ref<null | HeaderMenu>(null)
    const isMenuOpen = computed(
      () => openMenu.value !== null || isSidebarVisible.value
    )

    const openMenuModal = (menuName: HeaderMenu) => {
      if (openMenu.value !== null) {
        close()
      }
      openMenu.value = menuName
    }
    const close = () => {
      openMenu.value = null
    }

    const isFetching = computed(() => mediaStore.fetchState.isFetching)

    const resultsCount = computed(() => mediaStore.resultCount)
    const { getI18nCount } = useI18nResultsCount()
    /**
     * Additional text at the end of the search bar.
     * Shows the loading state or result count.
     */
    const searchStatus = computed(() => {
      if (!isSearchRoute.value || searchStore.searchTerm === '') return ''
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

      const searchType = isSearchRoute.value
        ? searchStore.searchType
        : ALL_MEDIA
      if (
        isSearchRoute.value &&
        (!searchTermChanged.value || searchTerm.value === '')
      )
        return
      if (searchTermChanged.value) {
        await mediaStore.clearMedia()

        searchStore.setSearchTerm(searchTerm.value)
        searchStore.setSearchType(searchType)
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

    return {
      closeIcon,
      isFetching,

      isHeaderScrolled,
      isDesktopLayout,
      isSearchRoute,
      headerHasTwoRows,
      areFiltersDisabled,

      openMenu,
      openMenuModal,
      isMenuOpen,

      menus,
      close,

      handleSearch,
      searchStatus,
      searchTerm,
    }
  },
})
</script>
