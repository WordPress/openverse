<template>
  <div class="browse-page">
    <div class="search columns">
      <div class="lg:hidden">
        <AppModal v-if="isFilterVisible" @close="onToggleSearchGridFilter">
          <SearchGridFilter />
        </AppModal>
      </div>
      <aside
        v-if="isFilterVisible"
        class="column is-narrow grid-sidebar is-hidden-touch max-w-full bg-white"
      >
        <SearchGridFilter />
      </aside>
      <div class="column search-grid-ctr">
        <SearchGridForm @onSearchFormSubmit="onSearchFormSubmit" />
        <SearchTypeTabs />
        <FilterDisplay v-show="shouldShowFilterTags" />
        <NuxtChild :key="$route.path" @onLoadMoreItems="onLoadMoreItems" />
        <ScrollButton
          data-testid="scroll-button"
          :show-btn="showScrollButton"
        />
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
import { screenWidth } from '~/utils/get-browser-info'
import { ALL_MEDIA, IMAGE, VIDEO } from '~/constants/media'
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex'
import { MEDIA, SEARCH } from '~/constants/store-modules'
import debounce from 'lodash.debounce'

const BrowsePage = {
  name: 'browse-page',
  layout({ store }) {
    return store.state.nav.isEmbedded ? 'embedded' : 'default'
  },
  scrollToTop: false,
  async fetch() {
    if (this.mediaType !== VIDEO && this.results.items.length === 0) {
      await this.fetchMedia({ mediaType: this.mediaType, q: this.query.q })
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

    const MIN_SCREEN_WIDTH_FILTER_VISIBLE_BY_DEFAULT = 800
    const isDesktop = () =>
      screenWidth() > MIN_SCREEN_WIDTH_FILTER_VISIBLE_BY_DEFAULT
    this.setFilterVisibility({
      isFilterVisible: isDesktop() ? localFilterState() : false,
    })
    window.addEventListener('scroll', this.debounceScrollHandling)
  },
  beforeDestroy() {
    window.removeEventListener('scroll', this.debounceScrollHandling)
  },
  computed: {
    ...mapState(SEARCH, ['query', 'isFilterVisible', 'searchType']),
    ...mapGetters(SEARCH, ['searchQueryParams', 'isAnyFilterApplied']),
    ...mapGetters(MEDIA, ['results']),
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
    async getMediaItems(params, mediaType) {
      await this.fetchMedia({ ...params, mediaType })
    },
    onLoadMoreItems(searchParams) {
      this.getMediaItems(searchParams, this.mediaType)
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
        this.getMediaItems(this.query, this.mediaType)
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
