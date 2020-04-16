<template>
  <div class="browse-page">
    <header-section />
    <div class="search columns">
      <div class="column is-narrow grid-sidebar is-paddingless" v-if="isFilterVisible">
        <search-grid-filter @onSearchFilterChanged="onSearchFormSubmit"/>
      </div>
      <div class="column search-grid-ctr">
        <search-grid-form @onSearchFormSubmit="onSearchFormSubmit" />
        <filter-display :query="query" />
      </div>
    </div>

    <footer-section></footer-section>
  </div>
</template>

<script>
import FooterSection from '@/components/FooterSection';
import HeaderSection from '@/components/HeaderSection';
import SearchGridForm from '@/components/SearchGridForm';
import SearchGridFilter from '@/components/SearchGridFilter';
import BrowsePageMixin from '@/pages/mixins/BrowsePageMixin';
import FilterDisplay from '@/components/FilterDisplay';
import ServerPrefetchProvidersMixin from '@/pages/mixins/ServerPrefetchProvidersMixin';

const BrowsePage = {
  components: {
    HeaderSection,
    SearchGridForm,
    FooterSection,
    SearchGridFilter,
  },
  mixins: [BrowsePageMixin, ServerPrefetchProvidersMixin],
};

export default BrowsePage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>

<style lang="scss">
  @import "../../styles/results-page.scss";
</style>
