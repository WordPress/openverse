<template>
  <div class="browse-page">
    <header-section />
    <div class="search columns">
      <div class="column is-narrow grid-sidebar" v-if="isFilterVisible">
        <search-grid-filter @onSearchFilterChanged="onSearchFormSubmit"/>
      </div>
      <div class="column search-grid-ctr">
        <search-grid-form @onSearchFormSubmit="onSearchFormSubmit" />
      </div>
    </div>

    <footer-section></footer-section>
  </div>
</template>

<script>
import FooterSection from '@/components/FooterSection';
import HeaderSection from '@/components/HeaderSection';
import SearchGridForm from '@/components/SearchGridForm';
import BrowsePageMixin from '@/pages/mixins/BrowsePageMixin';
import ServerPrefetchProvidersMixin from '@/pages/mixins/ServerPrefetchProvidersMixin';

const BrowsePage = {
  components: {
    HeaderSection,
    SearchGridForm,
    FooterSection,
  },
  mixins: [BrowsePageMixin, ServerPrefetchProvidersMixin],
};

export default BrowsePage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>

<style lang="scss">
  .search {
    margin-top: 0;
  }

  .search-grid-ctr {
    padding: 0;
    background: #e9ebee;
    min-height: 600px;
    margin: 0;
    transition: margin .7s ease-in-out;
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
