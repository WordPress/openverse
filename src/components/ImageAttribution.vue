<template>
  <section class="sidebar_section">
    <header class="sidebar_section-header">
      <h2>
        Image Attribution
      </h2>
    </header>
    <div >
      <div class="photo-attribution">
        <span id="attribution" class="photo_usage-attribution" ref="photoAttribution">
          <a :href="image.foreign_landing_url">"{{ image.title }}"</a>
          <span v-if="image.creator">
            by
            <a v-if="image.creator_url" :href="image.creator_url">{{ image.creator }}</a>
            <span v-else>{{ image.creator }}</span>
          </span>
          is licensed under
          <a class="photo_license" :href="ccLicenseURL">
          {{ fullLicenseName.toUpperCase() }}
          </a>
          <license-icons :image="image"></license-icons>
        </span>
        <CopyButton id="copy-attribution-btn"
                    el="#attribution"
                    title="Copy the attribution to paste into your blog or document"
                    @copied="onCopyAttribution">
          Copy
        </CopyButton>
      </div>
      <div class="embed-attribution">
        <span>Copy the HTML below to embed the attribution in your web page</span>
        <textarea id="attribution-html"
                  :value="attributionHtml"
                  cols="30" rows="4"
                  readonly="readonly">
        </textarea>
        <CopyButton id="embed-attribution-btn"
                    el="#attribution-html"
                    title="Copy the HTML to embed the attribution in your web page"
                    @copied="onEmbedAttribution">
          Copy HTML
        </CopyButton>
      </div>
      <reuse-survey />
      <legal-disclaimer :source="image.provider" :sourceURL="image.foreign_landing_url" />
    </div>
  </section>
</template>

<script>
import LicenseIcons from '@/components/LicenseIcons';
import CopyButton from '@/components/CopyButton';
import LegalDisclaimer from '@/components/LegalDisclaimer';
import ReuseSurvey from '@/components/ReuseSurvey';
import { COPY_ATTRIBUTION, EMBED_ATTRIBUTION } from '@/store/action-types';

export default {
  name: 'image-attribution',
  props: ['id', 'image', 'ccLicenseURL', 'fullLicenseName', 'attributionHtml'],
  components: {
    LicenseIcons,
    CopyButton,
    LegalDisclaimer,
    ReuseSurvey,
  },
  methods: {
    onCopyAttribution(e) {
      this.$store.dispatch(COPY_ATTRIBUTION, {
        content: e.content,
      });
    },
    onEmbedAttribution() {
      this.$store.dispatch(EMBED_ATTRIBUTION);
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../styles/photodetails.scss';
</style>
