<template>
  <div>
    <header-section></header-section>
    <div class="collections-page grid-container full">
      <h1>Browser our providers' collections</h1>
      <div class="providers-list grid-x">
        <div class="card provider-card cell small" v-for="(provider, index) in providers"
            :key="index">
          <div class="card-divider">
            <h2 class="provider-name">{{ provider.display_name }}</h2>
          </div>
          <div class="provider-logo">
            <a :href="'/collections/'+provider.provider_name">
              <img :alt="provider"
                  :src="getProviderLogo(provider.provider_name)">
            </a>
          </div>
          <div class="card-section">
            <span>Collection size: {{ getProviderImageCount(provider.image_count) }} images</span>
          </div>
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
    width: 15em;
    background-color: #dedede;
    margin: 0.5em;
  }

  .provider-name {
    font-size: 1.2em;
  }

  .provider-logo {
    height: 10em;
    line-height: 10em;
    white-space: nowrap;
    position: relative;

    a {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
    }

    img {
      width: 100%;
    }
  }
</style>
