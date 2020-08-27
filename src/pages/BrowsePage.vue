<template>
  <div class="browse-page">
    <header-section />
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
      <main role="main" class="column search-grid-ctr">
        <search-grid-form @onSearchFormSubmit="onSearchFormSubmit" />
        <search-type-tabs />
        <filter-display
          v-if="$route.path === '/search' || $route.path === '/search/image'"
          :query="query"
        />
        <router-view
          :query="query"
          @onLoadMoreImages="onLoadMoreImages"
          :key="$route.path"
        />
      </main>
    </div>
    <footer-section></footer-section>
  </div>
</template>
<script>
import FooterSection from '@/components/FooterSection'
import HeaderSection from '@/components/HeaderSection'
import SearchGrid from '@/components/SearchGrid'
import SearchGridForm from '@/components/SearchGridForm'
import SearchGridFilter from '@/components/Filters/SearchGridFilter'
import SearchTypeTabs from '@/components/SearchTypeTabs'
import FilterDisplay from '@/components/Filters/FilterDisplay'
import AppModal from '@/components/AppModal'
import { FETCH_IMAGES } from '../store/action-types'
import { SET_QUERY, SET_FILTER_IS_VISIBLE } from '../store/mutation-types'
import { ExperimentData } from '../abTests/experiments/filterExpansion'

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
  components: {
    HeaderSection,
    SearchGridForm,
    FilterDisplay,
    SearchGridFilter,
    SearchTypeTabs,
    SearchGrid,
    FooterSection,
    AppModal,
  },
}

export default BrowsePage
</script>

<style lang="scss" scoped>
@import '../styles/results-page.scss';
</style>
