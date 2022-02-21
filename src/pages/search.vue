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
          :media-results="results"
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
import { mapActions, mapGetters, mapState } from 'vuex'
import {
  FETCH_MEDIA,
  UPDATE_QUERY,
  SET_SEARCH_STATE_FROM_URL,
} from '~/constants/action-types'
import { ALL_MEDIA, supportedSearchTypes } from '~/constants/media'
import { MEDIA, SEARCH } from '~/constants/store-modules'
import { queryStringToSearchType } from '~/utils/search-query-transform'

import { inject } from '@nuxtjs/composition-api'
import { isMinScreen } from '~/composables/use-media-query.js'
import { useFilterSidebarVisibility } from '~/composables/use-filter-sidebar-visibility'

import VScrollButton from '~/components/VScrollButton.vue'
import VSearchGrid from '~/components/VSearchGrid.vue'
import VSkipToContentContainer from '~/components/VSkipToContentContainer.vue'

const BrowsePage = {
  name: 'browse-page',
  layout: 'default',
  components: {
    VScrollButton,
    VSearchGrid,
    VSkipToContentContainer,
  },
  setup() {
    const isMinScreenMd = isMinScreen('md')
    const { isVisible } = useFilterSidebarVisibility()
    const showScrollButton = inject('showScrollButton')

    return {
      isMinScreenMd,
      isVisible,
      showScrollButton,
    }
  },
  scrollToTop: false,
  async fetch() {
    if (this.supported && !this.resultCount && this.query.q.trim() !== '') {
      await this.fetchMedia({})
    }
  },
  async asyncData({ route, store }) {
    if (process.server) {
      await store.dispatch(`${SEARCH}/${SET_SEARCH_STATE_FROM_URL}`, {
        path: route.path,
        query: route.query,
      })
    }
  },
  computed: {
    ...mapState(SEARCH, ['query', 'searchType']),
    ...mapGetters(SEARCH, ['searchQueryParams', 'isAnyFilterApplied']),
    ...mapGetters(MEDIA, ['results', 'resultCount', 'fetchState']),
    mediaType() {
      return this.searchType ?? ALL_MEDIA
    },
    /**
     * Number of search results. Returns 0 for unsupported types.
     * @returns {number}
     */
    resultsCount() {
      return this.supported ? this.resultCount : 0 ?? 0
    },
    supported() {
      return supportedSearchTypes.includes(this.searchType)
    },
  },
  methods: {
    ...mapActions(MEDIA, { fetchMedia: FETCH_MEDIA }),
    ...mapActions(SEARCH, {
      setSearchStateFromUrl: SET_SEARCH_STATE_FROM_URL,
      updateQuery: UPDATE_QUERY,
    }),
    onSearchFormSubmit({ q }) {
      this.updateQuery({ q })
    },
  },
  watch: {
    /**
     * Updates the search type only if the route's path changes.
     * This watcher is important when changing the search type via All grid's ContentLink.
     * @param newRoute
     * @param oldRoute
     */
    $route(newRoute, oldRoute) {
      if (newRoute.path !== oldRoute.path) {
        const searchType = queryStringToSearchType(newRoute.path)
        this.updateQuery({ searchType })
      }
    },
  },
}

export default BrowsePage
</script>
