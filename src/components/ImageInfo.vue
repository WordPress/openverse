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
        <div>
          <a :href="image.foreign_landing_url"
              target="blank"
              rel="noopener noreferrer">
            <img class="provider-logo"
                :alt="image.source"
                :title="image.source"
                :src="getProviderLogo(image.source)" />
          </a>
      </div>
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
import getProviderLogo from '@/utils/getProviderLogo';

export default {
  name: 'image-info',
  props: ['image', 'ccLicenseURL', 'fullLicenseName', 'imageWidth', 'imageHeight'],
  components: {
    LicenseIcons,
  },
  methods: {
    getProviderLogo(providerName) {
      return getProviderLogo(providerName);
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../styles/photodetails.scss';
</style>
