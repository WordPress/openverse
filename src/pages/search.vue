<template>
  <div class="browse-page">
    <div class="search columns">
      <Component
        :is="searchFilter.as"
        v-if="isFilterVisible"
        :class="searchFilter.classes"
        @close="onToggleSearchGridFilter"
        ><SearchGridFilter
      /></Component>
      <div class="column search-grid-ctr">
        <SearchGridForm @onSearchFormSubmit="onSearchFormSubmit" />
        <SearchTypeTabs class="mb-4" />
        <FilterDisplay v-show="shouldShowFilterTags" />
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
              :is-filter-visible="isFilterVisible"
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
import { SET_FILTER_IS_VISIBLE } from '~/constants/mutation-types'
import { queryStringToSearchType } from '~/utils/search-query-transform'
import local from '~/utils/local'
import { ALL_MEDIA, AUDIO, IMAGE } from '~/constants/media'
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex'
import { MEDIA, SEARCH } from '~/constants/store-modules'
import debounce from 'lodash.debounce'

import { isScreen } from '~/composables/use-media-query.js'

import AppModal from '~/components/AppModal.vue'
import VScrollButton from '~/components/VScrollButton.vue'
import VSearchGrid from '~/components/VSearchGrid.vue'
import SearchGridFilter from '~/components/Filters/SearchGridFilter.vue'

const BrowsePage = {
  name: 'browse-page',
  layout: 'default',
  components: {
    AppModal,
    SearchGridFilter,
    VScrollButton,
    VSearchGrid,
  },
  setup() {
    const defaultWindow = typeof window !== 'undefined' ? window : undefined
    const isMdScreen = isScreen('md', defaultWindow)
    return {
      isMdScreen,
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
    const localFilterState = () =>
      local.get(process.env.filterStorageKey)
        ? local.get(process.env.filterStorageKey) === 'true'
        : true
    this.setFilterVisibility({
      isFilterVisible: this.isMdScreen && localFilterState(),
    })
    window.addEventListener('scroll', this.debounceScrollHandling)
  },
  beforeDestroy() {
    window.removeEventListener('scroll', this.debounceScrollHandling)
  },
  computed: {
    ...mapState(SEARCH, ['query', 'isFilterVisible', 'searchType']),
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
    ...mapMutations(SEARCH, {
      setFilterVisibility: SET_FILTER_IS_VISIBLE,
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
      this.setFilterVisibility({
        isFilterVisible: !this.isFilterVisible,
      })
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
  background-color: $color-wp-gray-0;
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
