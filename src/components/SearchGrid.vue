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
      <div v-for="(image, index) in images"
        :class="{ 'search-grid_item': true,
                  'search-grid_ctr__active': image.isActive
                }"
        :key="index"
        @click="onGotoDetailPage(image)">
        <span v-if='isActive'>is Active</span>
        <img class="search-grid_image" :src="image.thumbnail || image.src">
        <div class="search-grid_item-overlay">
          <a class="search-grid_overlay-title"
             :href="image.url"
             @click.stop="() => false"
             target="new">
             {{ image.title }}
          </a>
          <a class="search-grid_overlay-add"
             @click.stop="addToImageList(image)"
             v-if="includeAddToList">
          </a>
        </div>
      </div>
      <infinite-loading @infinite="infiniteHandler" v-if="useInfiniteScroll"></infinite-loading>
    </div>
  </section>
</template>

<script>
import { ADD_IMAGE_TO_LIST, SET_IMAGE_PAGE, SET_GRID_FILTER } from '@/store/mutation-types';
import { FETCH_IMAGES } from '@/store/action-types';
import InfiniteLoading from 'vue-infinite-loading';


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
    appliedFilters() {
      return this.$store.state.filter;
    },
    imagePage() {
      return this.$store.state.imagePage;
    },
    isFetching() {
      return this.$store.state.isFetching;
    },
  },
  watch: {
    isFetching() {
      if (this.$state) this.$state.loaded();
    },
  },
  data: () => ({
    isActive: false,
  }),
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
    addToImageList(image) {
      this.$store.commit(ADD_IMAGE_TO_LIST, { image });
    },
    infiniteHandler($state) {
      this.$state = $state;


      if (this.isFetching === false) {
        if( this.imagesCount < 20 ) {
          this.$store.commit(SET_IMAGE_PAGE,
            { imagePage: this.imagePage + 1 },
          );
        }

        this.$nextTick(() => {
          this.$store.dispatch(
            FETCH_IMAGES,
            { q: this.query,
              page: this.imagePage,
              shouldPersistImages: true,
              filter: this.appliedFilters,
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
  .search-grid_item {
    overflow: hidden;

    &:hover .search-grid_item-overlay {
      opacity: 1;
      bottom: 0%;
    }
  }

  .search-grid_item-overlay {
    opacity: 0;
    transition: all .4s ease;
    position: absolute;
    width: 100%;
    height: 20%;
    bottom: -100%;
    color: #fff;
    background: linear-gradient(to top, rgba(0,0,0,.5) 0, rgba(0,0,0,0) 100%);
    padding: 10px;
  }

  .search-grid_overlay-title {
    position: absolute;
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

  .infinite-loading-container {
    margin-top: 30px;
    width: 100%;
  }

  .search-grid_ctr__active {
    height: 0px !important;
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
    .search-grid_item {
      width: 100%;
      height: 100%;
    }
  }
</style>
