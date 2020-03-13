<template>
  <section class="sidebar_section">
    <!-- TODO: try to centralize contents in photo details page) -->
    <div >
      <div class="photo-attribution">
        <span id="attribution" class="photo_usage-attribution" ref="photoAttribution">
          <a :href="image.foreign_landing_url"
             target="_blank"
             rel="noopener"
             @click="onPhotoSourceLinkClicked">{{ imageTitle }}</a>
          <span v-if="image.creator">
            by
            <a v-if="image.creator_url"
               :href="image.creator_url"
               target="_blank"
               rel="noopener"
               @click="onPhotoCreatorLinkClicked">{{ image.creator }}</a>
            <span v-else>{{ image.creator }}</span>
          </span>
          is licensed under
          <a class="photo_license" :href="licenseURL" target="_blank" rel="noopener">
          {{ fullLicenseName.toUpperCase() }}
          </a>
        </span>
        <license-icons :image="image"></license-icons>
        <CopyButton id="copy-attribution-btn"
                    el="#attribution"
                    title="Copy the attribution to paste into your blog or document"
                    @copied="onCopyAttribution">
          Copy rich text
        </CopyButton>
      </div>
      <div class="embed-attribution">
        <span>
          Copy the HTML below to embed the attribution with license icons in your web page
        </span>
        <textarea id="attribution-html"
                  class="is-family-code"
                  :value="attributionHtml"
                  cols="30" rows="4"
                  readonly="readonly">
        </textarea>
        <CopyButton id="embed-attribution-btn"
                  el="#attribution-html"
                  title="Copy the HTML to embed the attribution with license icons in your web page"
                  @copied="onEmbedAttribution">
          Copy html
        </CopyButton>
      </div>
      <reuse-survey :image="image" />
      <legal-disclaimer
          :source="image.provider"
          :sourceProviderCode="image.provider_code"
          :sourceURL="image.foreign_landing_url" />
    </div>
  </section>
</template>

<script>
import LicenseIcons from '@/components/LicenseIcons';
import CopyButton from '@/components/CopyButton';
import LegalDisclaimer from '@/components/LegalDisclaimer';
import ReuseSurvey from '@/components/ReuseSurvey';
import { COPY_ATTRIBUTION, EMBED_ATTRIBUTION } from '@/store/action-types';
import { SEND_DETAIL_PAGE_EVENT, DETAIL_PAGE_EVENTS } from '@/store/usage-data-analytics-types';

export default {
  name: 'image-attribution',
  props: ['id', 'image', 'ccLicenseURL', 'fullLicenseName', 'attributionHtml'],
  components: {
    LicenseIcons,
    CopyButton,
    LegalDisclaimer,
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

<style lang="scss" scoped>
  @import '../styles/photodetails.scss';
</style>
