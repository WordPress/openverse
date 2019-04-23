<template>
  <section class="sidebar_section">
    <header class="sidebar_section-header">
      <h2>
        Image Attribution
      </h2>
    </header>
    <div class="grid-container fluid">
      <div class="grid-x grid-margin-x grid-margin-y">
        <div class="photo-attribution cell large-6">
          <p id="attribution" class="photo_usage-attribution" ref="photoAttribution">
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
          </p>
          <CopyButton id="copy-attribution-btn"
                      el="#attribution"
                      title="Can be used in WYSIWYG editors"
                      @copied="onCopyAttribution">
            Copy Attribution
          </CopyButton>
        </div>
        <div class="cell large-6">
          <span>Copy the HTML below to embed the attribution in your website</span>
          <textarea id="attribution-html"
                    :value="attributionHtml"
                    cols="30" rows="10"
                    readonly="readonly">
          </textarea>
          <CopyButton id="embed-attribution-btn"
                      el="#attribution-html"
                      title="Can be used in websites"
                      @copied="onEmbedAttribution">
            Copy
          </CopyButton>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import LicenseIcons from '@/components/LicenseIcons';
import CopyButton from '@/components/CopyButton';
import { COPY_ATTRIBUTION, EMBED_ATTRIBUTION } from '@/store/action-types';

export default {
  name: 'image-attribution',
  props: ['id', 'image', 'ccLicenseURL', 'fullLicenseName', 'attributionHtml'],
  components: {
    LicenseIcons,
    CopyButton,
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
