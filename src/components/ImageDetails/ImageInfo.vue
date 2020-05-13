<template>
  <section class="sidebar_section">
    <div class="margin-bottom-big">
      <h5 class="is-block margin-bottom-small b-header">Dimensions</h5>
      <span class="body-big">
        {{ imageWidth }} &times;  {{ imageHeight }} pixels
      </span>
    </div>
    <div class="margin-bottom-big">
      <h5 class="is-block margin-bottom-small b-header">Source</h5>
      <div class="body-big">
        <a :href="image.foreign_landing_url"
            target="blank"
            rel="noopener noreferrer">
          <img class="provider-logo"
              :alt="image.source"
              :title="image.source"
              :src="getProviderLogo(image.source)" />
        </a>
    </div>
    </div>
    <div class="margin-bottom-big">
      <h5 class="is-block margin-bottom-small b-header">License</h5>
      <license-icons :image="image"></license-icons>
      <a class="photo_license body-big" :href="ccLicenseURL">
      {{ fullLicenseName }}
      </a>
    </div>
    <div class="margin-bottom-big">
      <h5 class="is-block margin-bottom-small b-header">Tags</h5>
      <photo-tags :tags="image.tags" :showHeader="false" />
    </div>
  </section>
</template>

<script>
import PhotoTags from '@/components/PhotoTags';
import getProviderName from '@/utils/getProviderName';
import LicenseIcons from '@/components/LicenseIcons';
import getProviderLogo from '@/utils/getProviderLogo';

export default {
  name: 'image-info',
  props: ['image', 'ccLicenseURL', 'fullLicenseName', 'imageWidth', 'imageHeight'],
  components: {
    LicenseIcons,
    PhotoTags,
  },
  computed: {
    providerName() {
      return getProviderName(this.$store.state.imageProviders, this.$props.image.source);
    },
  },
  methods: {
    getProviderLogo(providerName) {
      return getProviderLogo(providerName);
    },
  },
};
</script>

<style lang="scss" scoped>
.report {
  font-size: 0.8rem !important;
  text-transform: none !important;

  &:hover {
    background: none !important;
  }

  &:focus {
    background: none !important;
  }
}
</style>
