<template>
  <section class="sidebar_section">
    <header class="sidebar_section-header">
      <h2>
        Image Download
      </h2>
    </header>
    <div class="large-12 cell">
      <fieldset class="large-7 cell">
        <div>
          <input
            id="watermark"
            type="checkbox"
            v-model="shouldWatermark" />
          <label for="watermark">
            Include attribution frame
          </label>
          <tooltip :tooltip="watermarkHelp" tooltipPosition="top">
            <span title="watermarkHelp">
              <img class='help-icon'
                    src='../assets/help_icon.svg'
                    alt='watermarkHelp' />
            </span>
          </tooltip>
        </div>
        <div>
          <input id="embedAttribution"
                  type="checkbox"
                  v-model="shouldEmbedMetadata" />
          <label for="embedAttribution">
            Embed attribution metadata
          </label>
          <tooltip :tooltip="metadataHelp" tooltipPosition="top">
            <span title="metadataHelp">
              <img class='help-icon'
                    src='../assets/help_icon.svg'
                    alt='metadataHelp' />
            </span>
          </tooltip>
        </div>
      </fieldset>
      <button class="button success download-watermark"
              data-type="text"
              @click="onDownloadWatermark(image, $event)">
          Download Image
      </button>
    </div>
  </section>
</template>

<script>
import Tooltip from '@/components/Tooltip';
import { DOWNLOAD_WATERMARK } from '@/store/action-types';

export default {
  name: 'watermark',
  props: ['image'],
  components: {
    Tooltip,
  },
  data: () => ({
    shouldEmbedMetadata: false,
    shouldWatermark: false,
    watermarkHelp: 'This option frames the image in white with a plain text attribution beneath.',
    metadataHelp: 'This option embeds attribution and CC license metadata in the image file using XMP.',
  }),
  computed: {
    watermarkURL() {
      return `${process.env.API_URL}/watermark/${this.image.id}?embed_metadata=${this.shouldEmbedMetadata}&watermark=${this.shouldWatermark}`;
    },
  },
  methods: {
    onDownloadWatermark(image) {
      const shouldEmbedMetadata = this.shouldEmbedMetadata;
      const shouldWatermark = this.shouldWatermark;
      this.$store.dispatch(DOWNLOAD_WATERMARK, {
        imageId: image.id,
        shouldWatermark,
        shouldEmbedMetadata,
      });
      window.location = this.watermarkURL;
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../styles/photodetails.scss';
</style>
