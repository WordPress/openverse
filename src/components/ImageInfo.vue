<template>
  <section class="sidebar_section">
    <header class="sidebar_section-header">
      <h2>
        Image Info
      </h2>
    </header>
    <ul>
      <li>
        <h3>Title</h3>
        <span>{{ image.title }}</span>
      </li>
      <li>
        <h3>Creator</h3>
        <span v-if="image.creator">
          <a v-if="image.creator_url" :href="image.creator_url">{{ image.creator }}</a>
          <span v-else>{{ image.creator }}</span>
        </span>
        <span v-else>
          Not Available
        </span>
      </li>
      <li>
        <h3>License</h3>
        <a class="photo_license" :href="ccLicenseURL">
        {{ fullLicenseName }}
        </a>
        <license-icons :image="image"></license-icons>
      </li>
      <li>
        <h3>Source</h3>
        <a class="photo_provider"
          :href="image.foreign_landing_url"
          target="blank"
          rel="noopener noreferrer">
          <img class="provider-logo" :alt="image.provider"
                  :src="getProviderLogo(image.provider_code)" />
        </a>
      </li>
      <li>
        <h3>Dimensions</h3>
        <span> {{ imageWidth }} <span> &times; </span> {{ imageHeight }} pixels</span>
      </li>
    </ul>
  </section>
</template>

<script>
import LicenseIcons from '@/components/LicenseIcons';
import ImageProviderService from '@/api/ImageProviderService';

export default {
  name: 'image-info',
  props: ['image', 'ccLicenseURL', 'fullLicenseName', 'imageWidth', 'imageHeight'],
  components: {
    LicenseIcons,
  },
  methods: {
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
  @import '../styles/photodetails.scss';
</style>
