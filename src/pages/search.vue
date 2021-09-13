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
        class="column is-narrow grid-sidebar is-hidden-touch"
      >
        <SearchGridFilter @onSearchFilterChanged="onSearchFormSubmit" />
      </aside>
      <div class="column search-grid-ctr">
        <SearchGridForm @onSearchFormSubmit="onSearchFormSubmit" />
        <SearchTypeTabs />
        <FilterDisplay v-if="shouldShowFilterTags" />
        <NuxtChild :key="$route.path" @onLoadMoreItems="onLoadMoreItems" />
      </div>
    </div>
  </div>
</template>
<script>
import {
  FETCH_MEDIA,
  SET_SEARCH_TYPE_FROM_URL,
} from '~/store-modules/action-types'
import {
  SET_QUERY,
  SET_FILTER_IS_VISIBLE,
  SET_FILTERS_FROM_URL,
} from '~/store-modules/mutation-types'
import { queryStringToQueryData } from '~/utils/search-query-transform'
import local from '~/utils/local'
import { screenWidth } from '~/utils/get-browser-info'
import iframeHeight from '~/mixins/iframe-height'
import i18nSync from '~/mixins/i18n-sync'
import { ALL_MEDIA, IMAGE } from '~/constants/media'

const BrowsePage = {
  name: 'browse-page',
  mixins: [iframeHeight, i18nSync],
  layout({ store }) {
    return store.state.isEmbedded ? 'embedded' : 'default'
  },
  scrollToTop: false,
  async fetch() {
    if (process.server) {
      const query = queryStringToQueryData(this.$route.fullPath)
      this.$store.commit(SET_QUERY, { query })
    }
    await this.$store.dispatch(SET_SEARCH_TYPE_FROM_URL, {
      url: this.$route.fullPath,
    })
    this.$store.commit(SET_FILTERS_FROM_URL, { url: this.$route.fullPath })
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
    mediaType() {
      // Default to IMAGE until media search/index is generalized
      return this.$store.state.searchType != ALL_MEDIA
        ? this.$store.state.searchType
        : IMAGE
    },
  },
  methods: {
    getMediaItems(params, mediaType) {
      this.$store.dispatch(FETCH_MEDIA, { ...params, mediaType })
    },
    onLoadMoreItems(searchParams) {
      this.getMediaItems(searchParams, this.mediaType)
    },
    onSearchFormSubmit(searchParams) {
      this.$store.commit(SET_QUERY, searchParams)
    },
    onToggleSearchGridFilter() {
      this.$store.commit(SET_FILTER_IS_VISIBLE, {
        isFilterVisible: !this.isFilterVisible,
      })
    },
    shouldShowFilterTags() {
      return (
        this.$route.path === '/search/' || this.$route.path === '/search/image'
      )
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
        this.getMediaItems(newQuery, this.mediaType)
      }
    },
  },
}

export default BrowsePage
</script>

<style lang="scss" scoped>
@import '~/styles/results-page.scss';
</style>
