<template>
  <div class="photo-detail-page grid-x">
    <div class="cell">
      <header-section showNavSearch="true" fixedNav="true"></header-section>
    </div>
    <div class="photo grid-x">
        <div class="photo_image-ctr cell medium-12 large-8">
          <img @click="onShowViewer"
               @load="() => isPrimaryImageLoaded = true"
               :class="{ photo_image: true,
                         'photo_image__has-viewer': this.images.length > 0 }"
                         :src="image.url">
        </div>
        <div class="photo_info-ctr cell medium-12 large-4">
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
              <span>
              <a :href="image.creator_url">{{ image.creator }}</a>
              </span>
            </li>
            <li>
              <h3>License</h3>
              <a :href="ccLicenseURL">
              CC {{ image.license }} {{ image.license_version }}
              </a>
            </li>
            <li>
              <h3>Source</h3>
              <a :href="image.foreign_landing_url">{{ image.provider }}</a>
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
              by
              <a :href="image.creator_url">{{ image.creator }}</a>
              is licensed under
              <a :href="ccLicenseURL">
              CC {{ image.license}} {{ image.license_version }}
              </a>
            </p>
            <button class="button photo_copy-btn
              photo_copy-btn__html"
              data-type="html">
            Copy to HTML</button>
            <button class="button
              photo_copy-btn
              photo_copy-btn__text"
              data-type="text">
            Copy to Text
            </button>
          </section>
      </div>
    </div>
    <div class="photo_tags grid-x full" v-if="tags">
      <header>
        <h2>Tags</h2>
      </header>
      <div class="photo_tags-ctr cell large-12">
        <template v-for="(tag, index) in image.tags">
          <span class="photo_tag button hollow secondary"
                :key="index"
                @click="onGotoSearchPage(tag.name)">
            <span class="photo_tag-label">
              <span>{{ tag.name }}</span>
            </span>
            <img class="photo_tag-provider-badge"
                 src="@/assets/clarifai_logo.png"
                 v-if="isClarifaiTag(tag.provider)">
          </span>
        </template>
        <p class="photo_tags-clarifai-badge" v-if="hasClarifaiTags">
          <span>Contains tags by</span>
          <a href="https://clarifai.com/">
            <img class="photo_tags-clarifai-badge-image" src="../assets/clarifai.svg" >
          </a>
        </p>
      </div>
    </div>
    <div class="photo_related-images grid-x" v-if="query">
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
import HeaderSection from '@/components/HeaderSection';
import FooterSection from '@/components/FooterSection';
import SearchGrid from '@/components/SearchGrid';
import { FETCH_IMAGE, FETCH_RELATED_IMAGES } from '@/store/action-types';
import Clipboard from 'clipboard';
import 'viewerjs/dist/viewer.css';
import Viewer from 'v-viewer';
import Vue from 'vue';

Vue.use(Viewer);

const PhotoDetailPage = {
  name: 'photo-detail-page',
  components: {
    HeaderSection,
    SearchGrid,
    FooterSection,
  },
  props: {
    id: '',
  },
  data: () => ({
    hasClarifaiTags: false,
    imagecountseparator: 'of',
    isPrimaryImageLoaded: false,
    keyinput: true,
    modalclose: true,
    mousescroll: true,
    showcaption: true,
    showclosebutton: true,
    showimagecount: true,
    showthumbnails: true,
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
      return this.$store.state.image.tags;
    },
    image() {
      return this.$store.state.image;
    },
    ccLicenseURL() {
      const image = this.image;
      const url = 'https://creativecommons.org/licenses';

      return `${url}/${image.license}/${image.license_version}`;
    },
    textAttribution() {
      const image = this.image;

      return `"${image.title}" by ${image.creator}
              is licensed under CC ${image.license}
              ${image.license_version}`;
    },
    HTMLAttribution() {
      const image = this.image;

      return `<a href="${image.foreign_landing_url}">"${image.title}"</a>
              by
              <a href="${image.creator_url}">${image.creator}</a>
              is licensed under
              <a href="${this.ccLicenseURL}">
                CC ${image.license} ${image.license_version}
              </a>`;
    },
    show() {
      const viewer = this.$el.querySelector('.images').$viewer;
      viewer.show();
    },
  },
  beforeRouteUpdate(to, from, next) {
    this.loadImage(to.params.id);
    next();
  },
  methods: {
    initClipboard() {
      new Clipboard('.photo_copy-btn', { // eslint-disable-line no-new
        text: (element) => {
          let attributionContent;
          if (element.getAttribute('data-type') === 'html') {
            attributionContent = this.HTMLAttribution;
          } else {
            attributionContent = this.textAttribution;
          }

          return attributionContent.replace(/\s\s/g, '');
        },
      });
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
    onGotoSearchPage(query) {
      this.$router.push({ name: 'browse-page', query: { q: query } });
    },
    onShowViewer() {
      if (this.images.length > 0) {
        const viewer = this.$refs.imageViewer.$viewer;
        viewer.show();
      }
    },
  },
  created() {
    this.loadImage(this.$route.params.id);
    this.initClipboard();
  },
  mounted() {
    const queryParam = this.query;

    if (queryParam) {
      this.$store.dispatch(FETCH_RELATED_IMAGES, { q: queryParam, pagesize: 8 });
    }
  },
};

export default PhotoDetailPage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  .photo_image__has-viewer {
    cursor: zoom-in;
  }

  .photo_image-viewer {
    display: none;
  }

  .photo-detail-page {
    width: 100%;
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
  }

  .photo {
    width: 100%;
    border-bottom: 1px solid #d6d6d6;
  }

  .photo_image-ctr {
    position: relative;
    text-align: center;
    padding: 30px;
    max-height: 640px;

    img {
      position: relative;
      width: auto;
      height: auto;
      max-height: 100%;
      max-width: 100%;
      background: #EBECE4;
    }

    /* Small only */
    @media screen and (max-width: 39.9375em) {
      padding: 30px 15px;
    }
  }

  .photo_info-ctr {
    padding: 45px 15px;
    border-left: 1px solid #d6d6d6;

    .photo_info-header {
      border-top: 1px solid #e7e8e9;
      margin-left: 15px;
    }

    h4 {
      font-size: 1.25rem;
      font-weight: 500;
      line-height: 1rem;
      margin: 0;
      padding: 0 0 0 15px;
    }

    h3 {
      font-size: 1rem;
      font-weight: 500;
      line-height: 1rem;
      margin: 0;
    }

    h2 {
      margin-bottom: 1.07142857em;
      font-size: .875em;
      font-weight: 600;
      letter-spacing: 1px;
      line-height: 1.25;
      text-transform: uppercase;
      display: inline-block;
      padding-top: .28571429em;
      border-top: 5px solid rgba(29, 31, 39, .8);
      margin-top: -3px;
    }

    ul {
      margin: 0;
      list-style-type: none;

      li {
        padding-left: 15px;
        margin-left: 0;
        margin-bottom: 10px;
      }
    }

    /* Small only */
    @media screen and (max-width: 39.9375em) {
      padding: 30px 0;
    }
  }

  .photo_usage {
    .photo_info-header {
      margin-left: 0px;
    }

    padding: 15px;
  }

  .photo_related-images,
  .photo_tags {
    margin: 30px;
    border-top: 1px solid #e7e8e9;

    header h2 {
      margin-bottom: 1.07142857em;
      width: 100%;
      font-size: 1em;
      font-weight: 600;
      letter-spacing: 1px;
      line-height: 1.25;
      text-transform: uppercase;
      display: inline-block;
      padding-top: .28571429em;
      border-top: 5px solid rgba(29, 31, 39, 0.8);
      margin-top: -3px;
    }

    /* Small only */
    @media screen and (max-width: 39.9375em) {
      margin: 15px;
    }
  }

  .photo_tag {
    margin-right: 15px;
    border-radius: 3px;
    padding: 10px 10px;
  }

  .photo_tag-label {
    font-weight: 500;
  }

  .photo_tag-provider-badge {
    width: 16px;
    margin-left: 5px;
  }

  .photo_tags-clarifai-badge-image {
    height: 100px;
    margin-left: -20px;
  }

  .photo_usage-attribution {
    border-left: 1px solid #e7e8e9;;
    padding-left: 10px;
    padding-bottom: 15px
  }

  .photo_copy-btn {
    border-radius: 3px;
    width: 49%;
  }

  .photo_copy-btn__html {
    background: #4A69CA;
  }

  .photo_copy-btn__text {
    background: #4A69CA;
  }
</style>
