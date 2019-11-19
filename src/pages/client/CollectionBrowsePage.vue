<template>
  <div class="browse-page">
    <div class="search grid-x flexible">
      <div class="cell">
        <header-section showNavSearch="true" />
      </div>
      <div class="cell small-3">
        <search-grid-filter isCollectionsPage="true"
                            :provider="provider"
                            @onSearchFilterChanged="onSearchFormSubmit"/>
      </div>
      <div class="cell auto search-grid-ctr">
        <search-grid-form @onSearchFormSubmit="onSearchFormSubmit"
                          searchBoxPlaceholder="Search this collection" />
        <search-grid v-if="query.provider"
                     :query="query"
                     :searchTerm="providerName"
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
import CollectionBrowseMixin from '@/pages/mixins/CollectionBrowseMixin';

const CollectionBrowsePage = {
  components: {
    HeaderSection,
    SearchGridForm,
    SearchGridFilter,
    SearchGrid,
    FooterSection,
  },
  mixins: [CollectionBrowseMixin],
};

export default CollectionBrowsePage;
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
