<template>
  <section class="sidebar_section">
    <div class="photo-attribution margin-bottom-big">
      <h5 class="b-header margin-bottom-big">License</h5>
      <span id="attribution" class="photo_usage-attribution is-block" ref="photoAttribution">
        This image was marked with a
        <a class="photo_license" :href="licenseURL" target="_blank" rel="noopener">
        {{ fullLicenseName.toUpperCase() }}
        </a>
        license.
      </span>
      <template v-for="(license, index) in splitLicenses">
        <license-explanations :licenseTerm="license" :key="index" />
      </template>

      <span class="caption has-text-weight-semibold">
        Read more about the license
        <a :href="licenseURL" target="_blank" rel="noopener">
        here
        </a>
      </span>
    </div>
    <reuse-survey :image="image" />
  </section>
</template>

<script>
import LicenseExplanations from '@/components/LicenseExplanations';
import { COPY_ATTRIBUTION, EMBED_ATTRIBUTION } from '@/store/action-types';
import { SEND_DETAIL_PAGE_EVENT, DETAIL_PAGE_EVENTS } from '@/store/usage-data-analytics-types';
import ReuseSurvey from './ReuseSurvey';

export default {
  name: 'image-attribution',
  props: ['id', 'image', 'ccLicenseURL', 'fullLicenseName', 'attributionHtml'],
  components: {
    LicenseExplanations,
    ReuseSurvey,
  },
  computed: {
    licenseURL() {
      return `${this.ccLicenseURL}&atype=rich`;
    },
    imageTitle() {
      const title = this.$props.image.title;
      return title !== 'Image' ? `"${title}"` : 'Image';
    },
    splitLicenses() {
      return this.$props.image.license.split('-');
    },
  },
  methods: {
    sendDetailPageEvent(eventType) {
      this.$store.dispatch(SEND_DETAIL_PAGE_EVENT, {
        eventType,
        resultUuid: this.$props.image.id,
      });
    },
    onCopyAttribution(e) {
      this.$store.dispatch(COPY_ATTRIBUTION, {
        content: e.content,
      });

      this.sendDetailPageEvent(DETAIL_PAGE_EVENTS.ATTRIBUTION_CLICKED);
    },
    onEmbedAttribution() {
      this.$store.dispatch(EMBED_ATTRIBUTION);

      this.sendDetailPageEvent(DETAIL_PAGE_EVENTS.ATTRIBUTION_CLICKED);
    },
    onPhotoSourceLinkClicked() {
      this.sendDetailPageEvent(DETAIL_PAGE_EVENTS.SOURCE_CLICKED);
    },
    onPhotoCreatorLinkClicked() {
      this.sendDetailPageEvent(DETAIL_PAGE_EVENTS.CREATOR_CLICKED);
    },
  },
};
</script>
