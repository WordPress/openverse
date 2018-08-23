<template>
  <section class='search-grid'>
    <div class="row">
      <div class="search-grid_analytics" v-if="includeAnalytics">
        <span>{{ this.$store.state.imagesCount }}</span>
        <span>{{ query }}</span>
        Photos
      </div>
      <div class="search-grid_layout-control"></div>
    </div>
    <ul class='search-grid_metrics-bar'>
      <li>What's</li>
      <li><a href="/browse/trending">trending</a></li>
      <li><a href="/browse/popular">popular</a></li>
      <li><a href="/browse/new">new</a></li>
    </ul>
    <div class="search-grid_ctr" ref="gridItems">
      <figure v-for="(image, index) in images"
        class="search-grid_item"
        :key="index"
        @click="onGotoDetailPage(image)">
        <a :href="image.foreign_landing_url"
             @click.prevent="() => false"
             target="new"
             class="search-grid_image-ctr">
          <img class="search-grid_image" :src="image.thumbnail || image.url" >
        </a>
        <figcaption class="search-grid_item-overlay">
          <a class="search-grid_overlay-title"
             :href="image.foreign_landing_url"
             @click.stop="() => false"
             target="new">
             {{ image.title }}
          </a>
          <a class="search-grid_overlay-add"
             @click.stop="onAddToImageList(image)"
             v-if="includeAddToList">
          </a>
        </figcaption>
      </figure>
      <infinite-loading
        @infinite="infiniteHandler"
        ref="infiniteLoader"
        v-if="useInfiniteScroll">
      </infinite-loading>
    </div>
  </section>
</template>

<script>
import { ADD_IMAGE_TO_LIST, SET_GRID_FILTER, SET_IMAGES } from '@/store/mutation-types';
import { FETCH_IMAGES } from '@/store/action-types';
import InfiniteLoading from 'vue-infinite-loading';

const DEFAULT_PAGE_SIZE = 20;

export default {
  name: 'search-grid',
  components: {
    InfiniteLoading,
  },
  props: {
    imagesCount: 0,
    images: {},
    query: null,
    filters: {},
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
    _filter() {
      return this.$store.state.filter;
    },
    imagePage() {
      return this.$store.state.imagePage;
    },
    imageCount() {
      return this.$store.state.imagesCount;
    },
    isFetching() {
      return this.$store.state.isFetching;
    },
    _query() {
      return this.$store.state.query;
    },
  },
  watch: {
    isFetching() {
      if (this.$state) this.$state.loaded();
    },
    _query: {
      handler() {
        this.searchChanged();
      },
      deep: true,
    },
    _filter: {
      handler() {
        this.searchChanged();
      },
      deep: true,
    },
  },
  methods: {
    created() {
      this.unsubscribe = this.$store.subscribe((mutation) => {
        if (mutation.type === SET_GRID_FILTER) {
          this.$store.dispatch(FETCH_IMAGES,
            { q: this.query, ...mutation.payload.filter },
          );
        }
      });
    },
    onGotoDetailPage(image) {
      this.$router.push(`/photos/${image.id}`);
    },
    onAddToImageList(image) {
      this.$store.commit(ADD_IMAGE_TO_LIST, { image });
    },
    searchChanged() {
      this.$store.commit(SET_IMAGES,
        { images: [] },
      );

      this.$nextTick(() => {
        this.$refs.infiniteLoader.$emit('$InfiniteLoading:reset');
      });
    },
    infiniteHandler($state) {
      this.$state = $state;

      if (this.isFetching === false) {
        if (this.imageCount < this.imagePage * DEFAULT_PAGE_SIZE) {
          this.$state.complete();

          return;
        }

        this.$nextTick(() => {
          this.$store.dispatch(
            FETCH_IMAGES,
            { q: this.query,
              page: this.imagePage + 1,
              shouldPersistImages: true,
              ...this._filter,
            },
          );
        });
      }
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
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
      bottom: 0%;
    }
  }

  .search-grid_item-overlay {
    position: absolute;
    opacity: 0;
    transition: all .4s ease;
    width: 100%;
    height: 30px;
    bottom: -100%;
    color: #fff;
    background: linear-gradient(to top, rgba(0,0,0,.5) 0, rgba(0,0,0,0) 100%);
    padding: 0 10px;
    display: block;
  }

  .search-grid_overlay-title {
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
    width: 100%;
    height: 100%;
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
  }
</style>
