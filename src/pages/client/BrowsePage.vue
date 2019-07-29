<template>
  <div class="browse-page">
    <div class="search grid-x flexible">
      <div class="cell">
        <header-section>
          <search-grid-form showProvidersFilter="true" @onSearchFormSubmit="onSearchFormSubmit" />
        </header-section>
      </div>
      <div :class="{ 'cell search-grid-ctr': true }">
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
import BrowsePageMixin from '@/pages/mixins/BrowsePageMixin';

const BrowsePage = {
  components: {
    HeaderSection,
    SearchGridForm,
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
