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

    <div class="margin-bottom-big">
      <button class="button is-text tiny is-paddingless report is-shadowless"
              @click="toggleReportFormVisibility()">
        <i class="icon flag"></i>
        <span class="margin-left-normal">Report this content</span>
      </button>
    </div>
    <div class="margin-bottom-big">
      <content-report-form v-if="isReportFormVisible"
                           :imageId="image.id"
                           :imageURL="image.foreign_landing_url" />
    </div>
  </section>
</template>

<script>
import { TOGGLE_REPORT_FORM_VISIBILITY } from '@/store/mutation-types';
import LicenseIcons from '@/components/LicenseIcons';
import ContentReportForm from '@/components/ContentReport/ContentReportForm';
import getProviderLogo from '@/utils/getProviderLogo';

export default {
  name: 'image-info',
  props: ['image', 'ccLicenseURL', 'fullLicenseName', 'imageWidth', 'imageHeight'],
  components: {
    LicenseIcons,
    ContentReportForm,
  },
  computed: {
    isReportFormVisible() {
      return this.$store.state.isReportFormVisible;
    },
  },
  methods: {
    getProviderLogo(providerName) {
      return getProviderLogo(providerName);
    },
    toggleReportFormVisibility() {
      this.$store.commit(TOGGLE_REPORT_FORM_VISIBILITY);
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
