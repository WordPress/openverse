<template>
  <section class='search-grid'>
    <div class="row">
      <div class="search-grid_analytics">
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
        :class="{ 'search-grid_item': true, 'search-grid_ctr__active': image.isActive }"
        :key="index"
        @mouseenter="onToggleOverlay(image, true)"
        @mouseleave="onToggleOverlay(image, false)">
        <img class="search-grid_image" :src="image.url">
        <div class="search-grid_item-overlay">
          <a @click.prevent="addToImageList(image)">+</a>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import { SET_IMAGES } from '@/store/mutation-types';
import { ADD_IMAGE_TO_LIST } from '@/store/mutation-types';

export default {
  name: 'search-grid',
  props: {
    imagesCount: 0,
    images: {},
    query: null,
  },
  data: () => ({
    isActive: false,
  }),
  methods: {
    onToggleOverlay(image, isActive) {
      image.isActive = isActive;
    },
    addToImageList(image) {
      this.$store.commit(ADD_IMAGE_TO_LIST, { image: image });
    }
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  .search-grid {
    margin: 30px 30px 60px 30px;
    min-height: 600px;
  }

  .search-grid_item-overlay {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    color: #fff;
    background: rgba( 0, 0, 0, .5);
    padding: 10px;

    a {
      color: #fff;
    }
  }

  .search-grid_metrics-bar {
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
