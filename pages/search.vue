<template>
  <div class="browse-page">
    <div class="search columns">
      <div class="is-hidden-desktop">
        <app-modal :visible="isFilterVisible" @close="onToggleSearchGridFilter">
          <search-grid-filter @onSearchFilterChanged="onSearchFormSubmit" />
        </app-modal>
      </div>
      <aside
        v-if="isFilterVisible"
        role="complementary"
        class="column is-narrow grid-sidebar is-paddingless is-hidden-touch"
        :class="filtersExpandedByDefault ? 'full-height-sticky' : ''"
      >
        <search-grid-filter @onSearchFilterChanged="onSearchFormSubmit" />
      </aside>
      <div class="column search-grid-ctr">
        <search-grid-form @onSearchFormSubmit="onSearchFormSubmit" />
        <search-type-tabs />
        <filter-display
          v-if="$route.path === '/search' || $route.path === '/search/image'"
          :query="query"
        />
        <nuxt-child
          :query="query"
          @onLoadMoreImages="onLoadMoreImages"
          :key="$route.path"
        />
      </div>
    </div>
  </div>
</template>
<script>
import { FETCH_IMAGES } from '../src/store/action-types'
import { SET_QUERY, SET_FILTER_IS_VISIBLE } from '../src/store/mutation-types'
import { ExperimentData } from '../src/abTests/experiments/filterExpansion'

const BrowsePage = {
  name: 'browse-page',
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
      this.$store.commit(SET_QUERY, { ...searchParams, shouldNavigate: true })
    },
    onToggleSearchGridFilter() {
      this.$store.commit(SET_FILTER_IS_VISIBLE, {
        isFilterVisible: !this.isFilterVisible,
      })
    },
  },
  mounted() {
    if (!this.$store.state.images.length) {
      this.getImages(this.query)
    }
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
@import '../src/styles/results-page.scss';
</style>
