<template>
  <div class="browse-page flex flex-col w-full search-grid-ctr">
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
  </div>
</template>

<script>
import {
  FETCH_MEDIA,
  UPDATE_QUERY,
  SET_SEARCH_STATE_FROM_URL,
  UPDATE_SEARCH_TYPE,
} from '~/constants/action-types'
import { ALL_MEDIA, AUDIO, IMAGE } from '~/constants/media'
import isEqual from 'lodash.isequal'
import { mapActions, mapGetters, mapState } from 'vuex'
import { MEDIA, SEARCH } from '~/constants/store-modules'

import { inject } from '@nuxtjs/composition-api'
import { isMinScreen } from '~/composables/use-media-query.js'
import { useFilterSidebarVisibility } from '~/composables/use-filter-sidebar-visibility'

import VScrollButton from '~/components/VScrollButton.vue'
import VSearchGrid from '~/components/VSearchGrid.vue'
import VFilterDisplay from '~/components/VFilters/VFilterDisplay.vue'

const BrowsePage = {
  name: 'browse-page',
  layout: 'default',
  components: {
    VFilterDisplay,
    VScrollButton,
    VSearchGrid,
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
    if (
      this.supported &&
      !Object.keys(this.results.items).length &&
      this.query.q.trim() !== ''
    ) {
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
    ...mapGetters(MEDIA, ['results', 'fetchState']),
    mediaType() {
      // Default to IMAGE until media search/index is generalized
      return this.searchType !== ALL_MEDIA ? this.searchType : IMAGE
    },
    /**
     * Number of search results. Returns 0 for unsupported types.
     * @returns {number}
     */
    resultsCount() {
      return this.supported ? this.results.count : 0
    },
    supported() {
      if (this.searchType === AUDIO) {
        // Only show audio results if non-image results are supported
        return process.env.enableAudio
      } else {
        return [IMAGE, ALL_MEDIA].includes(this.searchType)
      }
    },
  },
  methods: {
    ...mapActions(MEDIA, { fetchMedia: FETCH_MEDIA }),
    ...mapActions(SEARCH, {
      setSearchStateFromUrl: SET_SEARCH_STATE_FROM_URL,
      updateSearchType: UPDATE_SEARCH_TYPE,
      updateQuery: UPDATE_QUERY,
    }),
    async getMediaItems(params) {
      if (this.query.q.trim() !== '') {
        await this.fetchMedia({ ...params })
      }
    },
    onSearchFormSubmit({ q }) {
      this.updateQuery({ q })
    },
  },
  watch: {
    query: {
      handler(newQuery, oldQuery) {
        console.log('query changed')
        const newPath = this.localePath({
          path: `/search/${this.searchType === 'all' ? '' : this.searchType}/`,
          query: this.searchQueryParams,
        })
        this.$router.push(newPath)
        if (!isEqual(oldQuery, newQuery) && this.supported) {
          this.getMediaItems(this.query)
        }
      },
    },
    searchType: {
      // This fix is necessary only until All search page is merged
      handler(newQuery, oldQuery) {
        if (
          [ALL_MEDIA, IMAGE].includes(newQuery) &&
          [ALL_MEDIA, IMAGE].includes(oldQuery)
        ) {
          const newPath = this.localePath({
            path: `/search/${
              this.searchType === 'all' ? '' : this.searchType
            }/`,
            query: this.searchQueryParams,
          })
          this.$router.push(newPath)
        }
      },
    },
  },
}

export default BrowsePage
</script>

<style lang="scss" scoped>
.search-grid-ctr {
  min-height: 600px;
  padding: 0;

  @include mobile {
    width: 100%;
    flex: none;
  }
}
</style>
