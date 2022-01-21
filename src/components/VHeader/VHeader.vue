<template>
  <header
    class="flex py-4 px-4 md:px-7 items-stretch z-40 w-full bg-white md:gap-x-2 gap-y-4"
    :class="{
      'flex-wrap': isSearchRoute,
      'border-b border-white': !isHeaderScrolled && !isMenuOpen,
      'border-b border-dark-charcoal-20':
        isSearchRoute && (isHeaderScrolled || isMenuOpen),
      'justify-between': isSearchRoute,
      'justify-start': !isSearchRoute,
    }"
  >
    <div class="items-stretch flex" :class="{ 'one-third': isSearchRoute }">
      <NuxtLink
        to="/"
        class="rounded-sm ring-offset-1 focus:outline-none focus-visible:ring focus-visible:ring-pink -ms-2 inline-flex items-center hover:bg-yellow mr-auto"
        :class="{
          'pe-3 md:pe-0': isSearchRoute && !isHeaderScrolled,
          'md:pe-3': !isSearchRoute,
        }"
      >
        <VLogoLoader :status="isFetching ? 'loading' : 'idle'" />
        <OpenverseLogoText
          v-if="!isSearchRoute || (isSearchRoute && !isHeaderScrolled)"
          class="-ml-1 mt-1"
          :class="{ 'md:hidden': isSearchRoute }"
          width="95"
          height="15"
        />
      </NuxtLink>
    </div>

    <VSearchBar
      v-show="!isHomeRoute"
      v-model.trim="searchTerm"
      class="md:ms-0 lg:w-1/2 2xl:w-1/3"
      :class="{
        'order-4 md:order-none w-full md:w-auto':
          isSearchRoute && !isHeaderScrolled,
        'mx-auto md:me-auto': isSearchRoute,
        'w-2/3': isHeaderScrolled,
      }"
      @submit="handleSearch"
    >
      <span
        v-show="searchStatus"
        class="info font-semibold text-xs text-dark-charcoal-70 group-hover:text-dark-charcoal group-focus:text-dark-charcoal mx-4"
      >
        {{ searchStatus }}
      </span>
    </VSearchBar>

    <VHeaderMenu
      :is-search-route="isSearchRoute"
      :class="{ 'one-third': isSearchRoute }"
      @open="openMenuModal(menus.CONTENT_SWITCHER)"
      @close="close()"
    />
    <VHeaderFilter
      v-if="isSearchRoute"
      class="text-sr md:text-base"
      :class="{ 'one-third': isSearchRoute }"
      @open="openMenuModal(menus.FILTERS)"
      @close="close()"
    />
  </header>
</template>

<script>
import {
  computed,
  defineComponent,
  inject,
  provide,
  ref,
  useContext,
  useRouter,
  watch,
  watchEffect,
} from '@nuxtjs/composition-api'

import { MEDIA, SEARCH } from '~/constants/store-modules'
import {
  CLEAR_MEDIA,
  FETCH_MEDIA,
  UPDATE_QUERY,
} from '~/constants/action-types'
import { ALL_MEDIA, AUDIO, IMAGE } from '~/constants/media'
import { isMinScreen } from '~/composables/use-media-query'
import {
  useMatchSearchRoutes,
  useMatchHomeRoute,
} from '~/composables/use-match-routes'
import { useFilterSidebarVisibility } from '~/composables/use-filter-sidebar-visibility'

import closeIcon from '~/assets/icons/close.svg'
import OpenverseLogoText from '~/assets/icons/openverse-logo-text.svg?inline'

import VHeaderMenu from '~/components/VHeader/VHeaderMenu.vue'
import VHeaderFilter from '~/components/VHeader/VHeaderFilter.vue'
import VLogoLoader from '~/components/VLogoLoader/VLogoLoader.vue'
import VSearchBar from '~/components/VHeader/VSearchBar/VSearchBar.vue'

const i18nKeys = {
  [ALL_MEDIA]: {
    noResult: 'browse-page.all-no-results',
    result: 'browse-page.all-result-count',
    more: 'browse-page.all-result-count-more',
  },
  [AUDIO]: {
    noResult: 'browse-page.audio-no-results',
    result: 'browse-page.audio-result-count',
    more: 'browse-page.audio-result-count-more',
  },
  [IMAGE]: {
    noResult: 'browse-page.image-no-results',
    result: 'browse-page.image-result-count',
    more: 'browse-page.image-result-count-more',
  },
}
const menus = {
  FILTERS: 'filters',
  CONTENT_SWITCHER: 'content-switcher',
}

const VHeader = defineComponent({
  name: 'VHeader',
  components: {
    VHeaderFilter,
    VHeaderMenu,
    VLogoLoader,
    VSearchBar,
    OpenverseLogoText,
  },
  setup() {
    const { app, i18n, store } = useContext()
    const router = useRouter()

    const { matches: isSearchRoute } = useMatchSearchRoutes()
    const { matches: isHomeRoute } = useMatchHomeRoute()

    const isHeaderScrolled = inject('isHeaderScrolled')
    const isMinScreenMd = isMinScreen('md', { shouldPassInSSR: true })
    const headerHasTwoRows = inject('headerHasTwoRows')
    provide('isMinScreenMd', isMinScreenMd)

    const menuModalRef = ref(null)

    const { isVisible: isFilterVisible } = useFilterSidebarVisibility()

    /**
     * Set the active mobile menu view to the 'filters'
     * if the filter sidebar has been toggled open.
     */
    watch([isFilterVisible], ([isFilterVisible]) => {
      openMenu.value = isFilterVisible ? menus.FILTERS : null
    })

    /**
     * @type {import('@nuxtjs/composition-api').Ref<null|'filters'|'content-switcher'>}
     */
    const openMenu = ref(null)
    const isMenuOpen = computed(() => openMenu.value !== null)

    /**
     * @param {'filters'|'content-switcher'} menuName
     */
    const openMenuModal = (menuName) => {
      if (openMenu.value !== null) {
        close()
      }
      openMenu.value = menuName
    }
    const close = () => {
      openMenu.value = null
    }

    /**  @type {import('@nuxtjs/composition-api').ComputedRef<boolean>} */
    const isFetching = computed(() => {
      return store.getters['media/fetchState'].isFetching
    })

    /**
     * Return a text representation of the result count.
     * @param {number} count
     * @returns {string}
     */
    const mediaCount = (count) => {
      if (store.getters['media/unsupportedMediaType']) return ''

      const countKey =
        count === 0 ? 'noResult' : count >= 10000 ? 'more' : 'result'
      const i18nKey = i18nKeys[store.state.search.searchType][countKey]
      const localeCount = count.toLocaleString(i18n.locale)
      return i18n.tc(i18nKey, count, { localeCount })
    }

    /** @type {import('@nuxtjs/composition-api').ComputedRef<number>} */
    const resultsCount = computed(() => store.getters['media/resultCount'])

    /**
     * Status is hidden below the medium breakpoint.
     * It shows Loading... or Number of results on bigger screens.
     * @returns {string}
     */
    const setInitialStatus = () => {
      if (
        !isMinScreenMd.value ||
        !isSearchRoute.value ||
        store.state.search.query.q === ''
      )
        return ''
      if (isFetching.value) return i18n.t('header.loading')
      return mediaCount(resultsCount.value)
    }

    const searchStatus = ref(setInitialStatus())

    watchEffect(() => {
      if (isMinScreenMd.value) {
        if (isFetching.value) {
          searchStatus.value = i18n.t('header.loading')
        } else if (!isSearchRoute.value) {
          searchStatus.value = ''
        } else {
          searchStatus.value = mediaCount(resultsCount.value)
        }
      } else {
        searchStatus.value = ''
      }
    })

    const localSearchTerm = ref(store.state.search.query.q)
    const searchTerm = computed({
      get: () => localSearchTerm.value,
      set: async (value) => {
        localSearchTerm.value = value
      },
    })

    watch(
      () => store.state.search.query.q,
      (newSearchTerm) => {
        if (newSearchTerm !== localSearchTerm.value) {
          localSearchTerm.value = newSearchTerm
        }
      }
    )

    const handleSearch = async () => {
      /**
       * If search term hasn't changed, don't do anything on a search route,
       * and change path to search path (all content types) from other pages.
       * If is search route and search term hasn't changed: return
       * If is not search route and search term hasn't changed: set the search type to all, set path.
       * If is search route and search term changed: set the query, set path
       * If is not search route, and search term changed: set search type to all, set query, set path
       */
      const searchTermChanged =
        localSearchTerm.value !== store.state.search.query.q
      if (isSearchRoute.value && !searchTermChanged) return
      const searchType = store.state.search.searchType
      if (searchTermChanged) {
        await Promise.all(
          [IMAGE, AUDIO].map((mediaType) =>
            store.dispatch(`${MEDIA}/${CLEAR_MEDIA}`, { mediaType })
          )
        )
        await store.dispatch(`${SEARCH}/${UPDATE_QUERY}`, {
          q: localSearchTerm.value,
          searchType,
        })
      }
      const newPath = app.localePath({
        path: `/search/${searchType === 'all' ? '' : searchType}`,
        query: store.getters['search/searchQueryParams'],
      })
      router.push(newPath)

      await store.dispatch(`${MEDIA}/${FETCH_MEDIA}`, {
        ...store.getters['search/searchQueryParams'],
      })
    }

    return {
      closeIcon,
      isFetching,

      isHeaderScrolled,
      isMinScreenMd,
      headerHasTwoRows,

      isSearchRoute,
      isHomeRoute,

      menuModalRef,

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

export default VHeader
</script>
<style scoped>
@media (max-width: 767px) {
  .one-third {
    flex-grow: 1;
    flex-shrink: 0;
  }
}
</style>
