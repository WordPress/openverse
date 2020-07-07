<template>
  <div class="browse-page">
    <header-section />
    <div class="search columns">
      <div class="column is-narrow grid-sidebar is-paddingless" v-if="isFilterVisible">
        <search-grid-filter isCollectionsPage="true"
                            :provider="provider"
                            @onSearchFilterChanged="onSearchFormSubmit"/>
      </div>
      <div class="column search-grid-ctr">
        <search-grid-form @onSearchFormSubmit="onSearchFormSubmit"
                          searchBoxPlaceholder="Search this collection" />
        <search-type-tabs />
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
import SearchGridFilter from '@/components/Filters/SearchGridFilter';
import SearchTypeTabs from '@/components/SearchTypeTabs';
import CollectionBrowseMixin from '@/pages/mixins/CollectionBrowseMixin';

const CollectionBrowsePage = {
  components: {
    HeaderSection,
    SearchGridForm,
    SearchGridFilter,
    SearchGrid,
    SearchTypeTabs,
    FooterSection,
  },
  mixins: [CollectionBrowseMixin],
};

export default CollectionBrowsePage;
</script>

<style lang="scss" scoped>
  @import "../../styles/results-page.scss";
</style>
