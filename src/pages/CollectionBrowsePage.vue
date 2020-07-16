<template>
  <div class="browse-page">
    <header-section />
    <div class="search columns">
      <div
        class="column is-narrow grid-sidebar is-paddingless"
        v-if="isFilterVisible"
      >
        <search-grid-filter
          isCollectionsPage="true"
          :provider="provider"
          @onSearchFilterChanged="onSearchFormSubmit"
        />
      </div>
      <div class="column search-grid-ctr">
        <search-grid-form
          @onSearchFormSubmit="onSearchFormSubmit"
          searchBoxPlaceholder="Search this collection"
        />
        <search-grid
          v-if="query.provider"
          :query="query"
          :searchTerm="providerName"
          @onLoadMoreImages="onLoadMoreImages"
        ></search-grid>
      </div>
    </div>
    <footer-section></footer-section>
  </div>
</template>

<script>
import FooterSection from '@/components/FooterSection';
import HeaderSection from '@/components/HeaderSection';
import SearchGrid from '@/components/SearchGrid';
import SearchGridForm from '@/components/SearchGridForm';
import SearchGridFilter from '@/components/Filters/SearchGridFilter';
import SearchTypeTabs from '@/components/SearchTypeTabs';
import { FETCH_COLLECTION_IMAGES } from '@/store/action-types';
import { SET_COLLECTION_QUERY } from '@/store/mutation-types';
import getProviderName from '@/utils/getProviderName';

const CollectionBrowsePage = {
  name: 'collection-browse-page',
  props: ['provider'],
  computed: {
    query() {
      return {
        ...this.$store.state.query,
        provider: this.$props.provider,
      }
    },
    providerName() {
      return getProviderName(
        this.$store.state.imageProviders,
        this.$props.provider
      )
    },
    isFilterVisible() {
      return this.$store.state.isFilterVisible
    },
  },
  methods: {
    getImages(params) {
      this.$store.dispatch(FETCH_COLLECTION_IMAGES, params)
    },
    onLoadMoreImages(searchParams) {
      this.getImages(searchParams)
    },
    onSearchFormSubmit(searchParams) {
      this.$store.commit(SET_COLLECTION_QUERY, {
        ...searchParams,
        provider: this.$props.provider,
      })
    },
  },
  created() {
    if (this.query.provider) {
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
    SearchGridFilter,
    SearchGrid,
    SearchTypeTabs,
    FooterSection,
  },
}

export default CollectionBrowsePage
</script>

<style lang="scss" scoped>
@import '../styles/results-page.scss';
</style>
