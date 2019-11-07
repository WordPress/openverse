<template>
  <div class="browse-page grid-container full">
    <div>
      <header-section />
    </div>
    <div class="search grid-x flexible">
      <div class="cell medium-6 large-4">
        <search-grid-filter showProvidersFilter="true" @onSearchFilterChanged="onSearchFormSubmit"/>
      </div>
      <div class="cell medium-6 large-8 search-grid-ctr">
        <search-grid-form @onSearchFormSubmit="onSearchFormSubmit" />
        <search-grid v-if="query.q"
                     :query="query"
                     searchTerm=""
                     @onLoadMoreImages="onLoadMoreImages"></search-grid>
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

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>

<style lang="scss">
  .search-grid {
    margin: 30px 30px 60px 30px;
  }

  .search-grid-ctr {
    background: #e9ebee;
    min-height: 600px;
    margin: 0;
    transition: margin .7s ease-in-out;
  }

  .search-grid-ctr__filter-visible {
    margin-top: 30px;
  }
</style>
