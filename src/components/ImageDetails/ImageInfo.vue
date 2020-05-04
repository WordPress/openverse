<template>
  <section class="sidebar_section">
    <div class="margin-bottom-big">
      <h4 class="b-header">{{ image.title }}</h4>
    </div>
    <div class="margin-bottom-big">
      <span class="is-block margin-bottom-small">Creator</span>
      <span v-if="image.creator">
        <a class="body-big" v-if="image.creator_url" :href="image.creator_url">
          {{ image.creator }}
        </a>
        <span class="body-big" v-else>{{ image.creator }}</span>
      </span>
      <span class="body-big" v-else>
        Not Available
      </span>
    </div>
    <div class="margin-bottom-big">
      <span class="is-block margin-bottom-small">License</span>
      <license-icons :image="image"></license-icons>
      <a class="photo_license body-big" :href="ccLicenseURL">
      {{ fullLicenseName }}
      </a>
    </div>
    <div class="margin-bottom-big">
      <span class="is-block margin-bottom-small">Source</span>
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
      <span class="is-block margin-bottom-small">Dimensions</span>
      <span class="body-big">
        {{ imageWidth }} &times;  {{ imageHeight }} pixels
      </span>
    </div>
  </section>
</template>

<script>
import getProviderName from '@/utils/getProviderName';
import LicenseIcons from '@/components/LicenseIcons';
import getProviderLogo from '@/utils/getProviderLogo';

export default {
  name: 'image-info',
  props: ['image', 'ccLicenseURL', 'fullLicenseName', 'imageWidth', 'imageHeight'],
  components: {
    LicenseIcons,
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
