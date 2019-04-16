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
        <image-info :image="image"
                    :ccLicenseURL="ccLicenseURL"
                    :fullLicenseName="fullLicenseName"
                    :imageWidth="imageWidth"
                    :imageHeight="imageHeight" />
        <section class="sidebar_section">
          <image-attribution :image="image"
                             :ccLicenseURL="ccLicenseURL"
                             :fullLicenseName="fullLicenseName" />
          <copy-attribution-buttons :image="image"
                                    :ccLicenseURL="ccLicenseURL"
                                    :fullLicenseName="fullLicenseName" />
        </section>
        <watermark v-if="watermarkEnabled" :image="image" />
        <image-social-share v-if="socialSharingEnabled" :image="image" />
      </section>
    </div>
</template>

<script>
import CopyButton from '@/components/CopyButton';
import SocialShareButtons from '@/components/SocialShareButtons';
import ImageInfo from '@/components/ImageInfo';
import Watermark from '@/components/Watermark';
import ImageAttribution from '@/components/ImageAttribution';
import CopyAttributionButtons from '@/components/CopyAttributionButtons';
import ImageSocialShare from '@/components/ImageSocialShare';
import decodeData from '@/utils/decodeData';


export default {
  name: 'photo-details',
  props: ['image', 'breadCrumbURL', 'shouldShowBreadcrumb', 'query', 'imageWidth', 'imageHeight', 'watermarkEnabled', 'socialSharingEnabled'],
  components: {
    CopyButton,
    SocialShareButtons,
    ImageInfo,
    Watermark,
    ImageAttribution,
    CopyAttributionButtons,
    ImageSocialShare,
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
  },
  methods: {
    onGoBackToSearchResults() {
      this.$router.push({ name: 'browse-page', query: this.query });
    },
    onImageLoad(event) {
      this.$emit('onImageLoaded', event);
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
</style>

