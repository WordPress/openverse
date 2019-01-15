<template>
  <div class="photo-detail-page grid-x">
    <div class="cell">
      <header-section showNavSearch="true" fixedNav="true"></header-section>
    </div>
    <photo-details :image="image"
                   :breadCrumbURL="breadCrumbURL"
                   :shouldShowBreadcrumb="shouldShowBreadcrumb"
                   :query="query"
                   :imageWidth="imageWidth"
                   :imageHeight="imageHeight"
                   @onImageLoaded="onImageLoaded" />
    <photo-tags :tags="tags" />
    <div class="photo_related-images grid-x full" v-if="relatedImages && relatedImages.length > 0">
      <header>
        <h2>Related Images</h2>
      </header>
      <search-grid
        :imagesCount="imagesCount"
        :images="relatedImages"
        :query="query"
        :filter="filter"
        :includeAnalytics="false"
        :useInfiniteScroll="false"
        :includeAddToList="false"
        v-if="isPrimaryImageLoaded===true">
      </search-grid>
    </div>
    <footer-section></footer-section>
    <viewer :images="images" ref="imageViewer" v-if="isPrimaryImageLoaded===true">
      <div class="photo_image-viewer" v-viewer="{movable: false}">
        <img v-for="(image, index) in images" :src="image.url" :key="index">
      </div>
    </viewer>
  </div>
</template>

<script>
import PhotoDetails from '@/components/PhotoDetails';
import PhotoTags from '@/components/PhotoTags';
import HeaderSection from '@/components/HeaderSection';
import FooterSection from '@/components/FooterSection';
import SearchGrid from '@/components/SearchGrid';
import LicenseIcons from '@/components/LicenseIcons';
import { FETCH_IMAGE, FETCH_RELATED_IMAGES } from '@/store/action-types';
import 'viewerjs/dist/viewer.css';
import Viewer from 'v-viewer';
import Vue from 'vue';
import { SET_IMAGE } from '@/store/mutation-types';

Vue.use(Viewer);

const PhotoDetailPage = {
  name: 'photo-detail-page',
  components: {
    HeaderSection,
    SearchGrid,
    FooterSection,
    LicenseIcons,
    PhotoDetails,
    PhotoTags,
  },
  props: {
    id: '',
  },
  data: () => ({
    breadCrumbURL: '',
    hasClarifaiTags: false,
    imagecountseparator: 'of',
    isPrimaryImageLoaded: false,
    shouldShowBreadcrumb: false,
    imageWidth: 0,
    imageHeight: 0,
  }),
  computed: {
    filter() {
      return this.$store.state.query.filter;
    },
    images() {
      return this.$store.state.images;
    },
    imagesCount() {
      return this.$store.state.imagesCount;
    },
    query() {
      return this.$store.state.query.q;
    },
    relatedImages() {
      return this.$store.state.relatedImages;
    },
    tags() {
      return this.$store.state.image.tags.filter(tag => !!tag.name);
    },
    image() {
      return this.$store.state.image;
    },
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
        this.image.license_version = '1.0';
        url = `${BASE_URL}/publicdomain/zero/1.0/`;
      } else if (image.license === 'pdm') {
        url = `${BASE_URL}/publicdomain/mark/1.0/`;
      }

      return url;
    },
    textAttribution() {
      const image = this.image;
      const licenseURL =
        `<a href="${this.ccLicenseURL}">
          CC ${image.license.toUpperCase()} ${image.license_version}
         </a>`;

      return `"${image.title}" by ${image.creator}
              is licensed under CC ${image.license.toUpperCase()}
              ${image.license_version} ${licenseURL}`;
    },
    HTMLAttribution() {
      const image = this.image;

      return `<a href="${image.foreign_landing_url}">"${image.title}"</a>
              by
              <a href="${image.creator_url}">${image.creator}</a>
              is licensed under
              <a href="${this.ccLicenseURL}">
                CC ${image.license.toUpperCase()} ${image.license_version}
              </a>`;
    },
    show() {
      const viewer = this.$el.querySelector('.images').$viewer;
      viewer.show();
    },
  },
  watch: {
    tags: function tags(value) {
      this.getRelatedImages(value, this.queryParam);
    },
  },
  beforeRouteUpdate(to, from, next) {
    this.imageHeight = 0;
    this.imageWidth = 0;
    this.$store.commit(SET_IMAGE, { image: {} });
    this.loadImage(to.params.id);
    next();
  },
  beforeRouteEnter(to, previousPage, nextPage) {
    nextPage((_this) => {
      if (previousPage.name === 'browse-page') {
        _this.shouldShowBreadcrumb = true; // eslint-disable-line no-param-reassign
        _this.breadCrumbURL = `/search?q=${previousPage.query.q}`; // eslint-disable-line no-param-reassign
      }
    });
  },
  methods: {
    onImageLoaded(event) {
      this.imageWidth = event.target.naturalWidth;
      this.imageHeight = event.target.naturalHeight;
      this.isPrimaryImageLoaded = true;
    },
    getRelatedImages(tags, query) {
      let queryParam = query;
      const tagsParam = (tags || []).slice();

      if (tagsParam.length > 0) {
        queryParam = tagsParam.slice(0, 1).map(tag => tag.name).join(', ');
      }

      if (queryParam) {
        this.$store.dispatch(FETCH_RELATED_IMAGES, { q: queryParam, pagesize: 8 });
      }
    },
    isClarifaiTag(provider) {
      let isClarifaiTag = false;

      if (provider === 'clarifai') {
        isClarifaiTag = true;
        this.hasClarifaiTags = true;
      }

      return isClarifaiTag;
    },
    loadImage(id) {
      if (id) {
        this.$store.dispatch(FETCH_IMAGE, { id });
      }
    },
    onGotoBack() {
      this.$router.push({ name: 'browse-page', query: { q: this.query } });
    },
    onShowViewer() {
      if (this.images.length > 0) {
        const selectedImageID = this.$route.params.id;
        let selectedImageIndex = 0;
        this.images.forEach((image, index) => {
          if (parseInt(selectedImageID, 10) === parseInt(image.id, 10)) {
            selectedImageIndex = index;
          }
        });
        const viewer = this.$refs.imageViewer.$viewer;
        if (selectedImageIndex) {
          viewer.view(selectedImageIndex);
        }
        viewer.show();
      }
    },
  },
  created() {
    this.loadImage(this.$route.params.id);
  },
};

export default PhotoDetailPage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  .photo_image-viewer {
    display: none;
  }

  .photo-detail-page {
    width: 100%;
  }

  .photo_license {
    text-transform: uppercase;
  }

  .photo_paginator {
    position: absolute;
    display: block;
    width: 50px;
    height: 50px;
    z-index: 400;
    top: 50%;
    opacity: .5;
  }

  .photo_paginator__previous {
    left: 5px;
    background: url('../assets/arrow-icon_left.svg')
                center
                center
                no-repeat;
  }

  .photo_paginator__next {
    right: 5px;
    background: url('../assets/arrow-icon_right.svg')
                center
                center
                no-repeat;
  }

  .search-grid {
    margin: 0;
    width: 100%;
  }
</style>
