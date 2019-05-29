<template>
  <div>
    <header-section></header-section>
    <div class="collections-page grid-container full">
      <h1>Browser our providers' collections</h1>
      <h2>Featured providers</h2>
      <div class="providers-list grid-x">
        <collection-item class="card provider-card cell small"
                        v-for="(provider, index) in featuredProviders"
                        :key="index"
                        :provider="provider" />
      </div>
      <hr />
      <div class="providers-list grid-x">
        <collection-item class="card provider-card cell small"
                          v-for="(provider, index) in otherProviders"
                          :key="index"
                          :provider="provider" />
      </div>
    </div>
    <footer-section></footer-section>
  </div>
</template>

<script>
import CollectionItem from '@/components/CollectionItem';
import HeaderSection from '@/components/HeaderSection';
import FooterSection from '@/components/FooterSection';

const FEATURED_PROVIDERS = ['flickr', 'behance', 'met', 'clevelandmuseum'];

const CollectionsPage = {
  name: 'collections-page',
  components: {
    HeaderSection,
    FooterSection,
    CollectionItem,
  },
  computed: {
    featuredProviders() {
      if (this.providers) {
        return this.providers.filter(
          provider => FEATURED_PROVIDERS.indexOf(provider.provider_name) >= 0,
        );
      }
      return [];
    },
    otherProviders() {
      if (this.providers) {
        return this.providers.filter(
          provider => FEATURED_PROVIDERS.indexOf(provider.provider_name) === -1,
        );
      }
      return [];
    },
    providers() {
      return this.$store.state.imageProviders;
    },
  },
};

export default CollectionsPage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  h1 {
    margin-bottom: .44117647em;
    letter-spacing: initial;
    line-height: 1.25;
    text-transform: initial;
  }

  .collections-page {
    margin: 45px !important;
  }
</style>
