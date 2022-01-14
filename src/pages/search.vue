<template>
  <div class="browse-page">
    <div class="search columns">
      <Component
        :is="searchFilter.as"
        v-if="isFilterSidebarVisible"
        id="filter-sidebar"
        :class="searchFilter.classes"
        @close="onToggleSearchGridFilter"
        ><VSearchGridFilter @close="onToggleSearchGridFilter"
      /></Component>
      <div class="column search-grid-ctr">
        <SearchTypeTabs class="mb-4" />
        <VFilterDisplay v-show="shouldShowFilterTags" />
        <VSearchGrid
          :id="`tab-${searchType}`"
          role="tabpanel"
          :aria-labelledby="searchType"
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
              :is-filter-visible="isFilterSidebarVisible"
              :search-term="query.q"
              :supported="supported"
              data-testid="search-results"
            />
          </template>
        </VSearchGrid>
        <VScrollButton v-show="showScrollButton" data-testid="scroll-button" />
      </div>
    </div>
  </div>
</template>

<script>
import {
  FETCH_MEDIA,
  UPDATE_QUERY,
  SET_SEARCH_STATE_FROM_URL,
  UPDATE_SEARCH_TYPE,
} from '~/constants/action-types'
import { queryStringToSearchType } from '~/utils/search-query-transform'
import { ALL_MEDIA, AUDIO, IMAGE } from '~/constants/media'
import { mapActions, mapGetters, mapState } from 'vuex'
import { MEDIA, SEARCH } from '~/constants/store-modules'
import debounce from 'lodash.debounce'

import { isMinScreen } from '~/composables/use-media-query.js'
import { useFilterSidebarVisibility } from '~/composables/use-filter-sidebar-visibility'

import AppModal from '~/components/AppModal.vue'
import VScrollButton from '~/components/VScrollButton.vue'
import VSearchGrid from '~/components/VSearchGrid.vue'
import VSearchGridFilter from '~/components/VFilters/VSearchGridFilter.vue'
import VFilterDisplay from '~/components/VFilters/VFilterDisplay.vue'

const BrowsePage = {
  name: 'browse-page',
  layout: 'default',
  components: {
    AppModal,
    VFilterDisplay,
    VSearchGridFilter,
    VScrollButton,
    VSearchGrid,
  },
  setup() {
    const isMdScreen = isMinScreen('md')
    const { isFilterSidebarVisible, setFilterSidebarVisibility } =
      useFilterSidebarVisibility({ mediaQuery: isMdScreen })

    return {
      isMdScreen,
      isFilterSidebarVisible,

      setFilterSidebarVisibility,
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
  data: () => ({
    showScrollButton: false,
  }),
  async created() {
    this.debounceScrollHandling = debounce(this.checkScrollLength, 100)
    if (process.server) {
      await this.setSearchStateFromUrl({
        path: this.$route.path,
        query: this.$route.query,
      })
    }
  },
  mounted() {
    window.addEventListener('scroll', this.debounceScrollHandling)
  },
  beforeDestroy() {
    window.removeEventListener('scroll', this.debounceScrollHandling)
  },
  computed: {
    ...mapState(SEARCH, ['query', 'searchType']),
    ...mapGetters(SEARCH, ['searchQueryParams', 'isAnyFilterApplied']),
    ...mapGetters(MEDIA, ['results', 'fetchState']),
    mediaType() {
      // Default to IMAGE until media search/index is generalized
      return this.searchType !== ALL_MEDIA ? this.searchType : IMAGE
    },
    shouldShowFilterTags() {
      return (
        ['/search/', '/search/image'].includes(this.$route.path) &&
        this.isAnyFilterApplied
      )
    },
    /**
     * Number of search results. Returns 0 for unsupported types.
     * @returns {number}
     */
    resultsCount() {
      return this.supported ? this.results.count : 0
    },
    searchFilter() {
      return {
        classes: {
          'column is-narrow grid-sidebar max-w-full bg-white': this.isMdScreen,
        },
        as: this.isMdScreen ? 'aside' : AppModal,
      }
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
    onToggleSearchGridFilter() {
      this.setFilterSidebarVisibility(!this.isFilterSidebarVisible)
    },
    checkScrollLength() {
      this.showScrollButton = window.scrollY > 70
    },
  },
  watch: {
    query: {
      deep: true,
      handler() {
        const newPath = this.localePath({
          path: this.$route.path,
          query: this.searchQueryParams,
        })
        this.$router.push(newPath)
        if (this.supported) {
          this.getMediaItems(this.query)
        }
      },
    },
    /**
     * Updates the search type only if the route's path changes.
     * @param newRoute
     * @param oldRoute
     */
    $route(newRoute, oldRoute) {
      if (newRoute.path !== oldRoute.path) {
        const searchType = queryStringToSearchType(newRoute.path)
        this.updateSearchType({ searchType })
      }
    },
  },
}

export default BrowsePage
</script>

<style lang="scss" scoped>
.search {
  margin: 0;
}
.search-grid-ctr {
  min-height: 600px;
  padding: 0;

  @include mobile {
    width: 100%;
    flex: none;
  }
}
.grid-sidebar {
  padding: 0;
  border-right: 1px solid $color-transition-gray;
  width: 21.875rem;
}
</style>
