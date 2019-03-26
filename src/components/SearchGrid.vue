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
      <div class="search-grid_layout-control cell medium-6 large-6 shrink">
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
      <search-grid-cell v-for="(image) in _images"
        :key="image.id"
        :image="image"
        :includeAddToList="includeAddToList" />
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
import { SET_IMAGES } from '@/store/mutation-types';
import { FETCH_IMAGES } from '@/store/action-types';
import InfiniteLoading from 'vue-infinite-loading';
import SearchGridCell from '@/components/SearchGridCell';
import SearchGridFilter from '@/components/SearchGridFilter';

const DEFAULT_PAGE_SIZE = 20;

export default {
  name: 'search-grid',
  components: {
    InfiniteLoading,
    SearchGridFilter,
    SearchGridCell,
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
      }
      else {
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
    searchChanged() {
      this.showGrid = false;
      this.$store.commit(SET_IMAGES, { images: [] });
      this.currentPage = 0;
      this.$nextTick(() => {
        this.$refs.infiniteLoader.$emit('$InfiniteLoading:reset');
      });
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
<style lang="scss">

  .search-grid_analytics h5,
  .search-grid_layout-control h5 {
    padding-top: 1.36vh;
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

  .search-grid__contain-images .search-grid_image{
    max-height: 100%;
  }

  .search-grid_notification {
    width: 50%;
    margin: auto;
    font-weight: 500;
    text-align: center;
  }
</style>
