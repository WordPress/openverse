<template>
  <VSkipToContentContainer
    class="browse-page flex flex-col w-full px-4 md:px-10"
  >
    <VSearchGrid
      :fetch-state="fetchState"
      :query="query"
      :supported="supported"
      :search-type="searchType"
      :results-count="resultsCount"
      data-testid="search-grid"
    >
      <template #media>
        <NuxtChild
          :key="$route.path"
          :result-items="resultItems"
          :fetch-state="fetchState"
          :is-filter-visible="isVisible"
          :search-term="query.q"
          :supported="supported"
          data-testid="search-results"
        />
      </template>
    </VSearchGrid>
    <VScrollButton v-show="showScrollButton" data-testid="scroll-button" />
  </VSkipToContentContainer>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'
import { isShallowEqualObjects } from '@wordpress/is-shallow-equal'
import { computed, inject } from '@nuxtjs/composition-api'

import { FETCH_MEDIA } from '~/constants/action-types'
import { supportedSearchTypes } from '~/constants/media'
import { MEDIA } from '~/constants/store-modules'
import { isMinScreen } from '~/composables/use-media-query'
import { useFilterSidebarVisibility } from '~/composables/use-filter-sidebar-visibility'

import { useSearchStore } from '~/stores/search'

import VSearchGrid from '~/components/VSearchGrid.vue'
import VSkipToContentContainer from '~/components/VSkipToContentContainer.vue'
import VScrollButton from '~/components/VScrollButton.vue'

const BrowsePage = {
  name: 'browse-page',
  components: {
    VScrollButton,
    VSearchGrid,
    VSkipToContentContainer,
  },
  setup() {
    const isMinScreenMd = isMinScreen('md')
    const { isVisible } = useFilterSidebarVisibility()
    const showScrollButton = inject('showScrollButton')
    const searchStore = useSearchStore()

    const searchTerm = computed(() => searchStore.searchTerm)
    const searchType = computed(() => searchStore.searchType)
    const query = computed(() => searchStore.searchQueryParams)
    const supported = computed(() =>
      supportedSearchTypes.includes(searchType.value)
    )

    return {
      isMinScreenMd,
      isVisible,
      showScrollButton,
      searchTerm,
      searchType,
      supported,
      query,
      setSearchStateFromUrl: searchStore.setSearchStateFromUrl,
    }
  },
  scrollToTop: false,
  async fetch() {
    if (this.supported && !this.resultCount && this.searchTerm.trim() !== '') {
      await this.fetchMedia({})
    }
  },
  asyncData({ route, $pinia }) {
    if (process.server) {
      const searchStore = useSearchStore($pinia)
      searchStore.setSearchStateFromUrl({
        path: route.path,
        urlQuery: route.query,
      })
    }
  },
  computed: {
    ...mapGetters(MEDIA, ['resultCount', 'fetchState', 'resultItems']),
    /**
     * Number of search results. Returns 0 for unsupported types.
     * @returns {number}
     */
    resultsCount() {
      return this.supported ? this.resultCount : 0 ?? 0
    },
  },
  methods: {
    ...mapActions(MEDIA, { fetchMedia: FETCH_MEDIA }),
  },
  watch: {
    /**
     * Updates the search type only if the route's path changes.
     * @param {import('@nuxt/types').Context['route']} newRoute
     * @param {import('@nuxt/types').Context['route']} oldRoute
     */
    async $route(newRoute, oldRoute) {
      if (
        newRoute.path !== oldRoute.path ||
        !isShallowEqualObjects(newRoute.query, oldRoute.query)
      ) {
        const { query, path } = newRoute
        await this.setSearchStateFromUrl({ urlQuery: query, path })
        this.fetchMedia(this.searchQueryParams)
      }
    },
  },
}

export default BrowsePage
</script>
