<template>
    <div class="photo grid-x">
      <div class="photo_image-ctr cell medium-12 large-8">
        <a class="photo_breadcrumb"
           :href="breadCrumbURL"
           @click.prevent="onGoBackToSearchResults"
           v-if="shouldShowBreadcrumb">&#171; Back to search results</a>
        <img @load="onImageLoad"
             class="photo_image"
             :src="image.url"
             :alt="image.title">
      </div>
      <section class="photo_info-ctr cell medium-12 large-4">
        <header class="photo_info-header">
          <h2>
            PHOTO INFO
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
            <a class="photo_provider"
               :href="image.foreign_landing_url"
               target="blank"
               rel="noopener noreferrer">{{ image.provider }}</a>
          </li>
          <li>
            <h3>Dimensions</h3>
            <span> {{ imageWidth }} <span> X </span> {{ imageHeight }} pixels</span>
          </li>
        </ul>
        <section class="photo_usage">
          <header class="photo_info-header">
            <h2>
              Photo Attribution
            </h2>
          </header>
          <p class="photo_usage-attribution" ref="photoAttribution">
            <a :href="image.foreign_landing_url">"{{ image.title }}"</a>
            <span v-if="image.creator">
              by
              <a v-if="image.creator_url" :href="image.creator_url">{{ image.creator }}</a>
              <span v-else>{{ image.creator }}</span>
            </span>
            is licensed under
            <a class="photo_license" :href="ccLicenseURL">
            {{ fullLicenseName }}
            </a>
          </p>
          <CopyButton :toCopy="HTMLAttribution" contentType="html">Copy to HTML</CopyButton>
          <CopyButton :toCopy="textAttribution" contentType="text">Copy to Text</CopyButton>
        </section>
        <section class="photo_usage">
          <header class="photo_info-header">
            <h2>
              Actions
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
                    Incude attribution in frame
                  </label>
                  <span data-tooltip class="top"
                        tabindex="1"
                        title="Wrap image in a white frame and include attribution text">
                    <img class='help-icon'
                         src='../assets/help_icon.svg'
                         alt='Wrap image in a white frame and include attribution text' />
                  </span>
                </div>
                <div>
                  <input id="embedAttribution"
                          type="checkbox"
                          v-model="shouldEmbedMetadata" />
                  <label for="embedAttribution">
                    Embed attribution metadata
                  </label>
                </div>
              </fieldset>
              <button class="button success download-watermark"
                      data-type="text"
                      @click="onDownloadWatermark(image, $event)">
                  Download Image
              </button>
            </div>
          <div>
            <a class="add-to-list"
              @click.stop="onAddToImageList(image, $event)">
              Add to list
            </a>
          </div>
        </section>
      </section>
    </div>
</template>

<script>
import CopyButton from '@/components/CopyButton';
import LicenseIcons from '@/components/LicenseIcons';
import { SELECT_IMAGE_FOR_LIST } from '@/store/mutation-types';
import { DOWNLOAD_WATERMARK } from '@/store/action-types';
import decodeData from '@/utils/decodeData';

export default {
  name: 'photo-details',
  props: ['image', 'breadCrumbURL', 'shouldShowBreadcrumb', 'query', 'imageWidth', 'imageHeight'],
  components: {
    CopyButton,
    LicenseIcons,
  },
  data: () => ({
    shouldEmbedMetadata: false,
    shouldWatermark: false,
  }),
  computed: {
    ccLicenseURL() {
      if (!this.image) {
        return '';
      }

      const image = this.image;
      const BASE_URL = 'https://creativecommons.org';
      let url = `${BASE_URL}/licenses/${image.license}/${image.license_version}`;
      let license = '';

      if (image.license) {
        license = image.license;
      }

      if (license === 'cc0') {
        url = `${BASE_URL}/publicdomain/zero/1.0/`;
      }
      else if (image.license === 'pdm') {
        url = `${BASE_URL}/publicdomain/mark/1.0/`;
      }

      return url;
    },
    fullLicenseName() {
      const license = this.image.license;
      const version = this.image.license_version;

      return license === 'cc0' ? `${license} ${version}` : `CC ${license} ${version}`;
    },
    watermarkURL() {
      return `${process.env.API_URL}/watermark/${this.image.id}?embed_metadata=${this.shouldEmbedMetadata}&watermark=${this.shouldWatermark}`;
    },
    textAttribution() {
      return () => {
        const image = this.image;
        const licenseURL = this.ccLicenseURL;
        const byCreator = image.creator ? `by ${image.creator}` : ' ';

        return `"${image.title}" ${byCreator}
                is licensed under ${this.fullLicenseName.toUpperCase()}. To view a copy of this license, visit: ${licenseURL}`;
      };
    },
    HTMLAttribution() {
      return () => {
        const image = this.image;

        let byCreator;
        if (image.creator) {
          if (image.creator_url) {
            byCreator = `by <a href="${image.creator_url}">${image.creator}</a>`;
          }
          else {
            byCreator = `by ${image.creator}`;
          }
        }
        else {
          byCreator = ' ';
        }

        return `<a href="${image.foreign_landing_url}">"${image.title}"</a>
                ${byCreator}
                is licensed under
                <a href="${this.ccLicenseURL}">
                  ${this.fullLicenseName.toUpperCase()}
                </a>`;
      };
    },
  },
  methods: {
    onGoBackToSearchResults() {
      this.$router.push({ name: 'browse-page', query: this.query });
    },
    onImageLoad(event) {
      this.$emit('onImageLoaded', event);
    },
    onAddToImageList(image, event) {
      const imageWithDimensions = image || {};
      imageWithDimensions.pageX = event.pageX;
      imageWithDimensions.pageY = event.pageY;

      this.$store.commit(SELECT_IMAGE_FOR_LIST, { image: imageWithDimensions });
    },
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
  watch: {
    image() {
      const image = this.image;
      image.creator = decodeData(image.creator);
      image.title = decodeData(image.title);
    },
  },
};
</script>

<style lang="scss" scoped>
  @import '../styles/photodetails.scss';

  .add-to-list {
    &:before {
      height: 13px;
      width: 13px;
      content: '';
      background: url('../assets/plus-icon-black.svg') no-repeat;
      opacity: .5;
      display: inline-block;
    }
  }

  .download-watermark {
    background: #01a635;
    color: #fff;
  }

  .help-icon {
    height: 24px;
  }
</style>

