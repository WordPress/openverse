<template>
  <div class="browse-page">
    <header-section />
    <div class="search columns">
      <div
        class="column is-narrow grid-sidebar is-paddingless"
        v-if="isFilterVisible"
      >
        <search-grid-filter @onSearchFilterChanged="onSearchFormSubmit" />
      </div>
      <div class="column search-grid-ctr">
        <search-grid-form @onSearchFormSubmit="onSearchFormSubmit" />
        <filter-display :query="query" />
        <search-grid
          v-if="query.q"
          :query="query"
          searchTerm=""
          @onLoadMoreImages="onLoadMoreImages"
        />
      </div>
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
import FilterDisplay from '@/components/Filters/FilterDisplay'
import { FETCH_IMAGES } from '@/store/action-types'
import { SET_QUERY } from '@/store/mutation-types'
import ServerPrefetchProvidersMixin from '@/pages/mixins/ServerPrefetchProvidersMixin'

const BrowsePage = {
  name: 'browse-page',
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
  },
  mounted() {
    if (this.query.q && !this.$store.state.images.length) {
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
    SearchGrid,
    FooterSection,
  },
  mixins: [ServerPrefetchProvidersMixin],
}

export default BrowsePage
</script>

<style lang="scss" scoped>
@import '../styles/results-page.scss';
</style>
