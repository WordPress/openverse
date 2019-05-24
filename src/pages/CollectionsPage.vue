<template>
  <div class="grid-container full">
    <header-section></header-section>
    <div class="collections-page">
        <h1>Browser our providers' collections</h1>
      <div class="providers-list">
        <div class="card provider-card" v-for="(provider, index) in providers"
            :key="index">
          <span>{{ provider.display_name }}</span>
          <a :href="'/collections/'+provider.provider_name">
            <img class="search-grid_overlay-provider-logo" :alt="provider"
                    :src="getProviderLogo(provider.provider_name)">
          </a>
          <span>Collection size: {{ getProviderImageCount(provider.image_count) }} images</span>
        </div>
      </div>
    </div>
    <footer-section></footer-section>
  </div>
</template>

<script>
import ImageProviderService from '@/api/ImageProviderService';
import HeaderSection from '@/components/HeaderSection';
import FooterSection from '@/components/FooterSection';

const CollectionsPage = {
  name: 'collections-page',
  components: {
    HeaderSection,
    FooterSection,
  },
  computed: {
    providers() {
      return this.$store.state.imageProviders;
    },
  },
  methods: {
    getProviderImageCount(imageCount) {
      return (imageCount).toLocaleString('en');
    },
    getProviderLogo(providerName) {
      const provider = ImageProviderService.getProviderInfo(providerName);
      if (provider) {
        const logo = provider.logo;
        const logoUrl = require(`@/assets/${logo}`); // eslint-disable-line global-require, import/no-dynamic-require

        return logoUrl;
      }

      return '';
    },
  },
};

export default CollectionsPage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  h1 {
    margin-bottom: .44117647em;
    font-size: 2.125em;
    font-weight: normal;
    letter-spacing: initial;
    line-height: 1.25;
    text-transform: initial;
  }

  .collections-page {
    margin: 45px !important;
  }

  .provider-card {
    width: 300px;
    background-color: #dedede;
  }
</style>
