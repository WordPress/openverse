<template>
  <div class="column is-2 margin-small has-background-white provider-card">
    <div>
      <a :href="'/collections/'+provider.source_name"
         class="provider-name has-text-weight-normal has-text-black">
        {{ provider.display_name }}
      </a>
    </div>
    <div class="provider-logo">
      <a :href="'/collections/'+provider.source_name">
        <img :alt="provider.display_name"
            :src="getProviderLogo(provider.source_name)">
      </a>
    </div>
    <div>
      <span class="has-text-grey-light has-text-weight-semibold">
        Collection size: {{ getProviderImageCount(provider.image_count) }} images
      </span>
    </div>
  </div>
</template>

<script>
import ImageProviderService from '@/api/ImageProviderService';

export default {
  name: 'collection-item',
  props: ['provider'],
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
</script>

<style lang="scss" scoped>
  .provider-card {
    border: 2px solid rgb(216, 216, 216);
    &:hover{
      box-shadow: 10px 10px 2px -5px #E7E7E7;
    }
  }

  .provider-name {
    font-weight: 800;
  }

  .provider-logo {
    height: 12rem;
    white-space: nowrap;
    position: relative;

    a {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
    }

    img {
      max-height: 10rem;
    }
  }
</style>
