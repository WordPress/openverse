<template>
  <div class="browse-page">
    <header-section />
    <div class="search columns">
      <div class="column is-narrow grid-sidebar" v-if="isFilterVisible">
        <search-grid-filter @onSearchFilterChanged="onSearchFormSubmit"/>
      </div>
      <div class="column search-grid-ctr">
        <search-grid-form @onSearchFormSubmit="onSearchFormSubmit" />
        <search-grid v-if="query.q"
                     :query="query"
                     searchTerm=""
                     @onLoadMoreImages="onLoadMoreImages" />
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
import SearchGridFilter from '@/components/SearchGridFilter';
import BrowsePageMixin from '@/pages/mixins/BrowsePageMixin';

const BrowsePage = {
  components: {
    HeaderSection,
    SearchGridForm,
    SearchGridFilter,
    SearchGrid,
    FooterSection,
  },
  mixins: [BrowsePageMixin],
};

export default BrowsePage;
</script>

<style lang="scss" scoped>
  .search {
    margin: 0;
  }

  .search-grid-ctr {
    padding: 0;
    background: #e9ebee;
    min-height: 600px;

    /* 48em = 768px */
    @media (max-width: 49em) {
      width: 100%;
      flex: none;
    }
  }

  .search-grid-ctr__filter-visible {
    margin-top: 30px;
  }

  .grid-sidebar {
    padding-top: 0;
    background: #fafafa;
    width: 21.875rem;

    /* 48em = 768px */
    @media (max-width: 49em) {
      width: 100%;
    }
  }
</style>
