<template>
  <div class="photo columns is-desktop is-marginless">
    <div class="column is-three-fifths photo_image-ctr margin-top-normal">
      <a class="photo_breadcrumb is-block has-text-left margin-normal has-text-grey"
          :href="breadCrumbURL"
          @click.prevent="onGoBackToSearchResults"
          v-if="shouldShowBreadcrumb">
          <i class="icon chevron-left margin-right-small"></i> Back to search results
      </a>
      <img @load="onImageLoad"
            class="photo_image"
            :src="image.url"
            :alt="image.title">
    </div>
    <div class="column image-info">
      <section class="tabs" >
        <ul>
          <li :class="tabClass(0, 'tab')">
            <a href="#panel0" :aria-selected="activeTab == 0" @click.prevent="setActiveTab(0)">
              Info
            </a>
          </li>
          <li :class="tabClass(1, 'tab')">
            <a href="#panel1" :aria-selected="activeTab == 1" @click.prevent="setActiveTab(1)">
              Attribution
            </a>
          </li>
          <li :class="tabClass(2, 'a')" v-if="socialSharingEnabled">
            <a href="#panel2" :aria-selected="activeTab == 2" @click.prevent="setActiveTab(2)">
              Share
            </a>
          </li>
        </ul>
      </section>
      <section class="photo_info-ctr tabs-content">
        <div :class="tabClass(0, 'tabs-panel')">
          <image-info :image="image"
                      :ccLicenseURL="ccLicenseURL"
                      :fullLicenseName="fullLicenseName"
                      :imageWidth="imageWidth"
                      :imageHeight="imageHeight" />
        </div>
        <div :class="tabClass(1, 'tabs-panel')">
          <image-attribution :image="image"
                              :ccLicenseURL="ccLicenseURL"
                              :fullLicenseName="fullLicenseName"
                              :attributionHtml="attributionHtml()" />
        </div>
        <div :class="tabClass(2, 'tabs-panel')">
          <image-social-share v-if="socialSharingEnabled" :image="image" />
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import ImageInfo from '@/components/ImageInfo';
import Watermark from '@/components/Watermark';
import ImageAttribution from '@/components/ImageAttribution';
import ImageSocialShare from '@/components/ImageSocialShare';
import attributionHtml from '@/utils/attributionHtml';

export default {
  name: 'photo-details',
  props: ['image', 'breadCrumbURL', 'shouldShowBreadcrumb', 'query', 'imageWidth', 'imageHeight', 'socialSharingEnabled'],
  components: {
    ImageInfo,
    Watermark,
    ImageAttribution,
    ImageSocialShare,
  },
  data() {
    return {
      activeTab: 0,
    };
  },
  computed: {
    fullLicenseName() {
      const license = this.image.license;
      const version = this.image.license_version;

      if (license) {
        return license.toLowerCase() === 'cc0' ? `${license} ${version}` : `CC ${license} ${version}`;
      }
      return '';
    },
    ccLicenseURL() {
      return `${this.image.license_url}?ref=ccsearch`;
    },
  },
  methods: {
    onGoBackToSearchResults() {
      this.$router.push({ name: 'browse-page', query: this.query, params: { location: this.$route.params.location } });
    },
    onImageLoad(event) {
      this.$emit('onImageLoaded', event);
    },
    tabClass(tabIdx, tabClass) {
      return {
        [tabClass]: true,
        'is-active': tabIdx === this.activeTab,
      };
    },
    setActiveTab(tabIdx) {
      this.activeTab = tabIdx;
    },
    attributionHtml() {
      const licenseURL = `${this.ccLicenseURL}&atype=html`;
      return attributionHtml(this.image, licenseURL, this.fullLicenseName);
    },
  },
};
</script>

<style lang="scss">
  @import '../styles/photodetails.scss';
</style>

