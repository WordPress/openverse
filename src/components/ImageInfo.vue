<template>
  <section class="sidebar_section">
    <ul>
      <li>
        <h4 class="b-header">{{ image.title }}</h4>
      </li>
      <li>
        <span class="is-block margin-bottom-small">Creator</span>
        <span v-if="image.creator">
          <a v-if="image.creator_url" :href="image.creator_url">{{ image.creator }}</a>
          <span v-else>{{ image.creator }}</span>
        </span>
        <span v-else>
          Not Available
        </span>
      </li>
      <li>
        <span class="is-block margin-bottom-small">License</span>
        <license-icons :image="image"></license-icons>
        <a class="photo_license" :href="ccLicenseURL">
        {{ fullLicenseName }}
        </a>
      </li>
      <li>
        <span class="is-block margin-bottom-small">Source</span>
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
        <span class="is-block margin-bottom-small">Dimensions</span>
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
