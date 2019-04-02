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
        <section class="sidebar_section">
          <header class="sidebar_section-header">
            <h2>
              Image info
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
              <span> {{ imageWidth }} <span> &times; </span> {{ imageHeight }} pixels</span>
            </li>
          </ul>
        </section>
        <section class="sidebar_section">
          <header class="sidebar_section-header">
            <h2>
              Image attribution
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
          <h3>Copy as</h3>
          <div class="attribution-buttons">
            <CopyButton :toCopy="HTMLAttribution"
                        contentType="html"
                        title="Can be used in website code">
              HTML code
            </CopyButton>
            <CopyButton :toCopy="textAttribution"
                        contentType="text"
                        title="Can be used in static documents">
              Plain text
            </CopyButton>
            <CopyButton :toCopy="HTMLAttribution"
                        contentType="rtf"
                        title="Can be used in WYSIWYG editors">
              Rich text
            </CopyButton>
          </div>
        </section>
        <section v-if="watermarkEnabled" class="sidebar_section">
          <header class="sidebar_section-header">
            <h2>
              Image download
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
        <section class="sidebar_section">
          <header class="sidebar_section-header">
            <h2>
              Share
            </h2>
          </header>
          <social-share-buttons
            :shareURL="shareURL"
            :imageURL="imageURL"
            :shareText="shareText">
          </social-share-buttons>
        </section>
      </section>
    </div>
</template>

<script>
import CopyButton from '@/components/CopyButton';
import LicenseIcons from '@/components/LicenseIcons';
import SocialShareButtons from '@/components/SocialShareButtons';
import Tooltip from '@/components/Tooltip';
import decodeData from '@/utils/decodeData';
import { DOWNLOAD_WATERMARK } from '@/store/action-types';


export default {
  name: 'photo-details',
  props: ['image', 'breadCrumbURL', 'shouldShowBreadcrumb', 'query', 'imageWidth', 'imageHeight', 'watermarkEnabled'],
  components: {
    CopyButton,
    LicenseIcons,
    SocialShareButtons,
    Tooltip,
  },
  data: () => ({
    shouldEmbedMetadata: false,
    shouldWatermark: false,
    watermarkHelp: 'Wrap image in a white frame and include attribution text',
    metadataHelp: 'Embed attribution in an EXIF metadata attribute in the image file',
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
    shareURL() {
      return window.location.href;
    },
    imageURL() {
      return this.image.foreign_landing_url;
    },
    shareText() {
      return encodeURI(`I found an image @creativecommons: ${this.imageURL}`);
    },
  },
  methods: {
    onGoBackToSearchResults() {
      this.$router.push({ name: 'browse-page', query: this.query });
    },
    onImageLoad(event) {
      this.$emit('onImageLoaded', event);
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
  .download-watermark {
    background: #01a635;
    color: #fff;
  }

  label {
    margin-right: 8px;
  }

  .help-icon {
    height: 24px;
  }

  .attribution-buttons {
    margin-top: 8px;
  }
</style>

