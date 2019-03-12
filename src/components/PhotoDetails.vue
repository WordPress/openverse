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
                <a :href="image.creator_url">{{ image.creator }}</a>
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
              Photo Attribution
            </h2>
          </header>
          <p class="photo_usage-attribution" ref="photoAttribution">
            <a :href="image.foreign_landing_url">"{{ image.title }}"</a>
            <span v-if="image.creator">
              by
              <a :href="image.creator_url">{{ image.creator }}</a>
            </span>
            is licensed under
            <a class="photo_license" :href="ccLicenseURL">
            {{ fullLicenseName }}
            </a>
          </p>
          <CopyButton :toCopy="HTMLAttribution" contentType="html">Copy to HTML</CopyButton>
          <CopyButton :toCopy="textAttribution" contentType="text">Copy to Text</CopyButton>
        </section>
        <section class="sidebar_section">
          <header class="sidebar_section-header">
            <h2>
              Actions
            </h2>
          </header>
          <a class="add-to-list"
             @click.stop="onAddToImageList(image, $event)">
             Add to list
          </a>
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
import { SELECT_IMAGE_FOR_LIST } from '@/store/mutation-types';
import decodeData from '@/utils/decodeData';

export default {
  name: 'photo-details',
  props: ['image', 'breadCrumbURL', 'shouldShowBreadcrumb', 'query', 'imageWidth', 'imageHeight'],
  components: {
    CopyButton,
    LicenseIcons,
    SocialShareButtons,
  },
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
        const byCreator = image.creator ? `by <a href="${image.creator_url}">${image.creator}</a>` : ' ';

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
    }
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
</style>

