<template>
  <div class="browse-page">
    <div class="search columns">
      <div class="desk:hidden">
        <AppModal v-if="isFilterVisible" @close="onToggleSearchGridFilter">
          <SearchGridFilter @onSearchFilterChanged="onSearchFormSubmit" />
        </AppModal>
      </div>
      <aside
        v-if="isFilterVisible"
        class="column is-narrow grid-sidebar p-0 hidden desk:block full-height-sticky"
      >
        <SearchGridFilter @onSearchFilterChanged="onSearchFormSubmit" />
      </aside>
      <div class="column search-grid-ctr">
        <SearchGridForm @onSearchFormSubmit="onSearchFormSubmit" />
        <SearchTypeTabs />
        <FilterDisplay
          v-if="$route.path === '/search/' || $route.path === '/search/image'"
          :query="query"
        />
        <NuxtChild
          :key="$route.path"
          :query="query"
          @onLoadMoreImages="onLoadMoreImages"
        />
      </div>
    </div>
  </div>
</template>
<script>
import { FETCH_IMAGES } from '~/store-modules/action-types'
import {
  SET_QUERY,
  SET_FILTER_IS_VISIBLE,
} from '~/store-modules/mutation-types'
import { queryStringToQueryData } from '~/utils/searchQueryTransform'
import local from '~/utils/local'
import { screenWidth } from '~/utils/getBrowserInfo'
import iframeHeight from '~/mixins/iframeHeight'

const BrowsePage = {
  name: 'browse-page',
  mixins: [iframeHeight],
  layout({ store }) {
    return store.state.isEmbedded ? 'embedded' : 'default'
  },
  scrollToTop: false,
  async fetch() {
    if (process.server) {
      const query = queryStringToQueryData(this.$route.fullPath)
      this.$store.commit(SET_QUERY, { query })
    }

    if (!this.$store.state.images.length) {
      await this.$store.dispatch(FETCH_IMAGES, this.$store.state.query)
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

    this.$store.commit(SET_FILTER_IS_VISIBLE, {
      isFilterVisible: isDesktop() ? localFilterState() : false,
    })
  },
  computed: {
    query() {
      return this.$store.state.query
    },
    isFilterVisible() {
      return this.$store.state.isFilterVisible
    },
  },
  methods: {
    getImages(params) {
      this.$store.dispatch(FETCH_IMAGES, params)
    },
    onLoadMoreImages(searchParams) {
      this.getImages(searchParams)
    },
    onSearchFormSubmit(searchParams) {
      this.$store.commit(SET_QUERY, searchParams)
    },
    onToggleSearchGridFilter() {
      this.$store.commit(SET_FILTER_IS_VISIBLE, {
        isFilterVisible: !this.isFilterVisible,
      })
    },
  },
  watch: {
    query(newQuery) {
      if (newQuery) {
        const newPath = this.localePath({
          path: this.$route.path,
          query: this.$store.state.query,
        })
        this.$router.push(newPath)
        this.getImages(newQuery)
      }
    },
  },
}

export default BrowsePage
</script>

<style lang="scss" scoped>
@import '~/styles/results-page.scss';
</style>
