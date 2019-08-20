<template>
  <div class="browse-page">
    <div class="search grid-x flexible">
      <div class="cell">
        <header-section>
          <search-grid-form showProvidersFilter="true" @onSearchFormSubmit="onSearchFormSubmit" />
        </header-section>
      </div>
      <div :class="{ 'cell search-grid-ctr': true }">
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
