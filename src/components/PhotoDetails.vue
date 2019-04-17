<template>
  <div class="photo">
    <div class="photo_image-ctr">
      <a class="photo_breadcrumb"
          :href="breadCrumbURL"
          @click.prevent="onGoBackToSearchResults"
          v-if="shouldShowBreadcrumb">&#171; Back to search results</a>
      <img @load="onImageLoad"
            class="photo_image"
            :src="image.url"
            :alt="image.title">
    </div>
    <section>
      <ul class="tabs" data-tabs id="example-tabs">
        <li :class="tabClass(0, 'tabs-title')">
          <a href="#panel0" :aria-selected="activeTab == 0" @click.prevent="setActiveTab(0)">
            <img class='tab-icon'
                 src='../assets/cc-by-icon_large.png'
                 alt='Image Attribution' />
          </a>
        </li>
        <li :class="tabClass(1, 'tabs-title')">
          <a href="#panel1" :aria-selected="activeTab == 1" @click.prevent="setActiveTab(1)">
            <img class='tab-icon'
                 src='../assets/info-icon.svg'
                 alt='Image Info' />
          </a>
        </li>
        <li :class="tabClass(2, 'tabs-title')" v-if="watermarkEnabled">
          <a href="#panel2" :aria-selected="activeTab == 2" @click.prevent="setActiveTab(2)">
            <img class='tab-icon'
                 src='../assets/download-icon.svg'
                 alt='Image Download' />
          </a>
        </li>
        <li :class="tabClass(3, 'tabs-title')" v-if="socialSharingEnabled">
          <a href="#panel3" :aria-selected="activeTab == 3" @click.prevent="setActiveTab(3)">
            <img class='tab-icon'
                 src='../assets/share-icon.svg'
                 alt='Share Image' />
          </a>
        </li>
      </ul>
    </section>
    <section class="photo_info-ctr tabs-content">
      <div :class="tabClass(0, 'tabs-panel')">
        <copy-attribution-buttons :image="image"
                                  :ccLicenseURL="image.license_url"
                                  :fullLicenseName="fullLicenseName" />
      </div>
      <div :class="tabClass(1, 'tabs-panel')">
        <image-info :image="image"
                    :ccLicenseURL="image.license_url"
                    :fullLicenseName="fullLicenseName"
                    :imageWidth="imageWidth"
                    :imageHeight="imageHeight" />
      </div>
      <div :class="tabClass(2, 'tabs-panel')">
        <watermark v-if="watermarkEnabled" :image="image" />
      </div>
      <div :class="tabClass(3, 'tabs-panel')">
        <image-social-share v-if="socialSharingEnabled" :image="image" />
      </div>
    </section>
  </div>
</template>

<script>
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
    ImageInfo,
    Watermark,
    ImageAttribution,
    CopyAttributionButtons,
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
    tabClass(tabIdx, tabClass) {
      return {
        [tabClass]: true,
        'is-active': tabIdx === this.activeTab,
      };
    },
    setActiveTab(tabIdx) {
      this.activeTab = tabIdx;
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

