<template>
  <div class="browse-page">
    <div class="search columns">
      <div class="is-hidden-desktop">
        <AppModal :visible="isFilterVisible" @close="onToggleSearchGridFilter">
          <SearchGridFilter @onSearchFilterChanged="onSearchFormSubmit" />
        </AppModal>
      </div>
      <aside
        v-if="isFilterVisible"
        role="complementary"
        class="column is-narrow grid-sidebar is-paddingless is-hidden-touch"
        :class="filtersExpandedByDefault ? 'full-height-sticky' : ''"
      >
        <SearchGridFilter @onSearchFilterChanged="onSearchFormSubmit" />
      </aside>
      <div class="column search-grid-ctr">
        <SearchGridForm @onSearchFormSubmit="onSearchFormSubmit" />
        <SearchTypeTabs />
        <FilterDisplay
          v-if="$route.path === '/search' || $route.path === '/search/image'"
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
import { ExperimentData } from '~/abTests/experiments/filterExpansion'

const BrowsePage = {
  name: 'browse-page',
  async fetch() {
    const { q, ...filters } = this.$route.query
    const query = { q }
    console.info(filters)
    this.$store.commit(SET_QUERY, { query })

    if (!this.$store.state.images.length) {
      await this.$store.dispatch(FETCH_IMAGES, query)
    }
  },
  asyncData() {},
  computed: {
    query() {
      return this.$store.state.query
    },
    isFilterVisible() {
      return this.$store.state.isFilterVisible
    },
    filtersExpandedByDefault() {
      const experiment = this.$store.state.experiments.find(
        (exp) => exp.name === ExperimentData.EXPERIMENT_NAME
      )
      return experiment
        ? experiment.case === ExperimentData.FILTERS_EXPANDED_CASE
        : false
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
