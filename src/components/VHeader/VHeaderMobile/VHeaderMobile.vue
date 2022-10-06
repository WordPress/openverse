<template>
  <header
    class="main-header z-30 flex w-full items-center justify-between gap-x-2 bg-white px-4 py-3 md:items-stretch md:py-4 md:px-7"
    :class="{
      'border-b border-white': !isHeaderScrolled && !isMenuOpen,
      'border-b border-dark-charcoal-20': isHeaderScrolled || isMenuOpen,
    }"
  >
    <VLogoButton :is-fetching="isFetching" :is-search-route="isSearchRoute" />

    <VSearchBar
      v-model.trim="searchTerm"
      class="flex-grow"
      size="medium"
      @submit="handleSearch"
    >
      <span
        v-show="searchStatus"
        class="info mx-4 hidden whitespace-nowrap text-xs font-semibold text-dark-charcoal-70 group-hover:text-dark-charcoal group-focus:text-dark-charcoal"
      >
        {{ searchStatus }}
      </span>
    </VSearchBar>
    <VContentSettingsModal :is-fetching="isFetching" />
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

import { IsHeaderScrolledKey, IsMinScreenMdKey } from '~/types/provides'

import VLogoButton from '~/components/VHeader/VLogoButton.vue'
import VModal from '~/components/VModal/VModal.vue'
import VSearchBar from '~/components/VHeader/VSearchBar/VSearchBar.vue'

import VContentSettingsModal from '~/components/VHeader/VHeaderMobile/VContentSettingsModal.vue'

import closeIcon from '~/assets/icons/close.svg'

const menus = {
  FILTERS: 'filters',
  CONTENT_SWITCHER: 'content-switcher',
}
type HeaderMenu = 'filters' | 'content-switcher'

/**
 * The mobile search header component.
 */
export default defineComponent({
  name: 'VHeaderMobile',
  components: {
    VContentSettingsModal,
    VLogoButton,
    VSearchBar,
  },
  setup() {
    const contentSettingsModalRef = ref<InstanceType<typeof VModal> | null>(
      null
    )
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()
    const { app } = useContext()
    const i18n = useI18n()
    const router = useRouter()

    const { matches: isSearchRoute } = useMatchSearchRoutes()

    const isHeaderScrolled = inject(IsHeaderScrolledKey)
    const isMinScreenMd = inject(IsMinScreenMdKey)

    const openMenu = ref<null | HeaderMenu>(null)
    const isMenuOpen = computed(() => openMenu.value !== null)

    const openMenuModal = (menuName: HeaderMenu) => {
      if (openMenu.value !== null) {
        close()
      }
      openMenu.value = menuName
    }
    const close = () => {
      openMenu.value = null
    }
    const closeModal = () => {
      if (contentSettingsModalRef.value) {
        contentSettingsModalRef.value.close()
      }
      close()
    }

    const isFetching = computed(() => {
      return mediaStore.fetchState.isFetching
    })

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
      const mediaStore = useMediaStore()
      const searchStore = useSearchStore()
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
      isMinScreenMd,
      isSearchRoute,
      areFiltersDisabled,

      contentSettingsModalRef,

      closeModal,
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
