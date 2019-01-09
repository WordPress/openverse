<template>
  <section :class="{ 'search-grid': true, 'search-grid__contain-images': shouldContainImages }"
           ref="searchGrid">
    <div class="grid-x" v-show="showGrid && includeAnalytics">
      <div class="search-grid_analytics cell medium-6 large-6" >
        <h5>
          <span>{{ _imagesCount }}</span>
          <span>{{ searchTerm }}</span>
          Photos
        </h5>
      </div>
      <div class="search-grid_layout-control cell medium-6 large-6">
        <h5>Grid Options:</h5>
        <fieldset>
          <input
            id="watermark"
            type="checkbox"
            v-model="shouldContainImages">
            <label for="watermark">
              Contain image
            </label>
        </fieldset>
      </div>
    </div>
    <ul class="search-grid_metrics-bar">
      <li>What's</li>
      <li><a href="/browse/trending">trending</a></li>
      <li><a href="/browse/popular">popular</a></li>
      <li><a href="/browse/new">new</a></li>
    </ul>
    <div class="search-grid_ctr" ref="gridItems">
      <figure v-for="(image) in _images"
        class="search-grid_item"
        :key="image.id"
        @click="onGotoDetailPage(image)">
        <a :href="image.foreign_landing_url"
          @click.prevent="() => false"
          target="new"
          class="search-grid_image-ctr">
          <img class="search-grid_image" :alt="image.title" :src="getImageUrl(image)"
               @error="onImageLoadError">
        </a>
        <figcaption class="search-grid_item-overlay search-grid_item-overlay__top">
          <license-icons :image="image"></license-icons>
        </figcaption>
        <figcaption class="search-grid_item-overlay search-grid_item-overlay__bottom">
          <a class="search-grid_overlay-provider"
             :href="image.foreign_landing_url"
             @click.stop="() => false"
             target="new">
             <img class="search-grid_overlay-provider-logo" :alt="image.provider"
                  :src="getProviderLogo(image.provider)">
             {{ image.title }}
          </a>
          <a class="search-grid_overlay-add"
             @click.stop="onAddToImageList(image, $event)"
             v-if="includeAddToList">
          </a>
        </figcaption>
      </figure>
      <infinite-loading
        @infinite="onInfiniteHandler"
        ref="infiniteLoader"
        v-if="useInfiniteScroll && isDataInitialized">
      </infinite-loading>
      <div class="search-grid_notification callout alert" v-if="isFetchingImagesError">
          <h5>Error fetching images</h5>
      </div>
    </div>
  </section>
</template>

<script>
import { SELECT_IMAGE_FOR_LIST, SET_IMAGES } from '@/store/mutation-types';
import { FETCH_IMAGES } from '@/store/action-types';
import ImageProviderService from '@/api/ImageProviderService';
import InfiniteLoading from 'vue-infinite-loading';
import LicenseIcons from '@/components/LicenseIcons';
import SearchGridFilter from '@/components/SearchGridFilter';


const errorImage = require('@/assets/404-grid_placeholder.png');

const DEFAULT_PAGE_SIZE = 20;

export default {
  name: 'search-grid',
  components: {
    InfiniteLoading,
    SearchGridFilter,
    LicenseIcons,
  },
  data: () => ({
    isDataInitialized: false,
    shouldContainImages: false,
    currentPage: 1,
    showGrid: false,
  }),
  props: {
    imagesCount: 0,
    images: {
      default: () => ([]),
    },
    query: {},
    useInfiniteScroll: {
      default: true,
    },
    includeAnalytics: {
      default: true,
    },
    includeAddToList: {
      default: true,
    },
  },
  computed: {
    imagePage() {
      return this.$store.state.imagePage;
    },
    isFetchingImagesError() {
      return this.$store.state.isFetchingImagesError;
    },
    isFetchingImages() {
      return this.$store.state.isFetchingImages;
    },
    searchTerm() {
      return this.$store.state.query.q;
    },
    _images() {
      return this.useInfiniteScroll ? this.$store.state.images : this.images;
    },
    _imagesCount() {
      return this.useInfiniteScroll ? this.$store.state.imagesCount : this.imagesCount;
    },
    _query() {
      return this.useInfiniteScroll ? this.$store.state.query : this.query;
    },
  },
  watch: {
    isFetchingImages: function handler(isFetchingImages) {
      if (isFetchingImages) {
        this.showGrid = false;
      } else {
        this.showGrid = true;
      }
    },
    _images: {
      handler() {
        if (this.$state) {
          this.$state.loaded();

          if (this._imagesCount < this.currentPage * DEFAULT_PAGE_SIZE) {
            this.$state.complete();
          }
        }

        this.isDataInitialized = true;
      },
    },
    _query: {
      handler() {
        this.searchChanged();
      },
      deep: true,
    },
  },
  methods: {
    getImageUrl(image) {
      if (!image) {
        return '';
      }

      let url = image.thumbnail || image.url;

      if (url.indexOf('http') === -1) {
        url = `https://${url}`;
      }

      return url;
    },
    getProviderLogo(providerName) {
      const logo = ImageProviderService.getProviderInfo(providerName).logo;
      const logUrl = require(`@/assets/${logo}`); // eslint-disable-line global-require, import/no-dynamic-require

      return logUrl;
    },
    onGotoDetailPage(image) {
      this.$router.push(`/photos/${image.id}`);
    },
    onAddToImageList(image, event) {
      const imageWithDimensions = image || {};
      imageWithDimensions.pageX = event.pageX;
      imageWithDimensions.pageY = event.pageY;

      this.$store.commit(SELECT_IMAGE_FOR_LIST, { image: imageWithDimensions });
    },
    searchChanged() {
      this.showGrid = false;
      this.$store.commit(SET_IMAGES, { images: [] });
      this.currentPage = 0;
      this.$nextTick(() => {
        this.$refs.infiniteLoader.$emit('$InfiniteLoading:reset');
      });
    },
    onImageLoadError(event) {
      const image = event.target;
      image.src = errorImage;
    },
    onInfiniteHandler($state) {
      this.$state = $state;

      if (this.isFetchingImages === false) {
        this.currentPage = this.currentPage + 1;
        const searchParams = Object.assign(
          { page: this.currentPage, shouldPersistImages: true },
          this._query,
        );

        this.$nextTick(() => {
          this.$store.dispatch(FETCH_IMAGES, searchParams);
        });
      }
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>

  .search-grid_analytics h5,
  .search-grid_layout-control h5 {
    font-size: 1rem;
    display: inline-block;
  }

  .search-grid_layout-control h5 {
    margin-right: 10px;
  }

  .search-grid_layout-control {
    text-align: right;

    fieldset {
      display: inline;
      margin-right: 5px;
    }
  }

  .infinite-loading-container {
    margin-top: 30px;
    width: 100%;
  }

  .search-grid_image-ctr {
    background: #EBECE4;
    display: block;
    width: 100%;
    height: 100%;
    min-height: 200px;
  }

  .search-grid_item {
    overflow: hidden;

    &:hover .search-grid_item-overlay {
      opacity: 1;
      bottom: 0;
    }

    &:hover .search-grid_item-overlay__top {
      top: 0;
    }
  }

  .search-grid_item-overlay {
    position: absolute;
    opacity: 0;
    transition: all .4s ease;
    width: 100%;
    height: 30px;
    color: #fff;
    padding: 0 10px;
    display: block;
    top: -100%;

    &__top {
      transition: all .5s ease;
      background: linear-gradient(to bottom,
                  rgba(0,0,0,.5)
                  0,
                  rgba(0,0,0,0) 100%);
      top: 0;
    }

    &__bottom {
      height: 30px;
      background: linear-gradient(to top,
                  rgba(0,0,0,.5)
                  0,
                  rgba(0,0,0,0) 100%);
      bottom: -100%;
      top: auto;
    }
  }

  .search-grid_overlay-provider {
    width: calc( 100% - 30px );
    display: block;
    bottom: 10px;
    left: 10px;
    z-index: 100;
    color: #fff;

    &:hover {
      text-decoration: underline;
    }
  }

  .search-grid_overlay-provider-logo {
    max-height: 30px;
    max-width: 40px;
    margin-right: 5px;
  }

  .search-grid_overlay-add {
    position: absolute;
    width:  18px;
    height: 18px;
    display: block;
    bottom: 10px;
    right: 10px;
    z-index: 100;

    &:after {
      height: 100%;
      width: 100%;
      display: block;
      content: '';
      background: url('../assets/plus-icon.svg') no-repeat;
      background-size: 18px;
      background-position: center center;
      opacity: .5;
    }

    &:hover:before {
      position: absolute;
      right: -5px;
      bottom: 25px;
      height: 20px;
      line-height: 20px;
      width: 80px;
      display: block;
      content: 'Add image to list';
      color: #fff;
      text-shadow: 0 0 2px rgba(0,0,0,.5);
      text-align:center;
      font-size: .6em;
      border-radius: 1px;
      background: rgba(0,0,0,.7);

      opacity: 1;
    }

    &:hover:after {
      opacity: .9;
    }
  }

  .search-grid_metrics-bar {
    display: none;

    margin: 15px 0 30px 0;

    li {
      display: inline-block;
      padding: 0;
      margin: 0;

      a:hover {
        border-bottom: 1px solid #1779ba;
      }

      &:after {
        content: ' | ';
      }

      &:last-of-type:after {
        content: '';
      }
    }
  }

  .photo-license-icons {
    opacity: .7;
    margin-top: 2px;
    height: 22px !important;

    &:hover {
      opacity: 1;
    }
  }

  .search-grid:after {
    content: '';
    display: block;
    clear: both;
  }

  .search-grid_ctr {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: flex-start;
    align-content: stretch;
    padding: 0;
  }

  .search-grid_item {
    position: relative;
    display: block;
    float: left;
    flex: 0 0 auto;
    flex-grow: 1;
    margin: 15px 15px 0 0;
    cursor: pointer;
  }

  .search-grid_image {
    margin: auto;
    display: block;
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
  }

  .search-grid__contain-images .search-grid_image{
    max-height: 100%;
  }

  .search-grid_notification {
    width: 50%;
    margin: auto;
    font-weight: 500;
    text-align: center;
  }

  @media screen and (min-width: 769px) {
    .search-grid_item {
      width: calc(100%/3.5);
      height: calc(100%/3.5);
      max-height: 200px;
      overflow: hidden;
    }
  }

  @media screen and (min-width: 601px) and (max-width: 768px) {
    .search-grid_item {
      width: calc(100%/2);
      height: calc(100%/2);
    }
  }

  @media screen and (max-width: 600px) {
    .search-grid_item-overlay {
      position: absolute;
      opacity: 1;
      bottom: 0;
    }

    .search-grid_item {
      width: 100%;
      height: 100%;
    }

    .search-grid_overlay-add {
      position: absolute;
      width:  44px;
      height: 44px;
      bottom: 0;
    }

     .search-grid_layout-control {
      text-align: left !important;
    }
  }
</style>
