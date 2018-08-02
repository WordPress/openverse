<template>
<section class='search-grid'>
  <ul class='search-grid_metrics-bar'>
    <li>What's</li>
    <li><a href="/browse/trending">trending</a></li>
    <li><a href="/browse/popular">popular</a></li>
    <li><a href="/browse/new">new</a></li>
  </ul>
  <div class="row">
    <div class="search-grid_analytics"></div>
    <div class="search-grid-layout-control"></div>
  </div>
  <div class="grid-items" ref="gridItems">
    <div class="grid-item"
      v-for="(image, index) in data"
      @click="gotoBrowsePage(image.identifier)"
      :key="index">
      <img :src="image.url">
    </div>
  </div>
</section>
</template>

<script>
import Packery from 'packery';

export default {
  name: 'search-grid',
  props: {
    data: {},
  },
  methods: {
    addData(data, options = {}) {
      if (options.render) {
        this.grid.render();
      }
    },
  },
  mounted() {
    window.setTimeout(() => {
      this.grid = new Packery('.grid-items', {
        itemSelector: '.grid-item',
        gutter: 10,
      });
    }, 1000);
  },
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  .search-grid {
    margin: 30px 30px 60px 30px;
    min-height: 600px;
  }

  .search-grid_metrics-bar {
    margin: 0;

    li {
      display: inline-block;
      padding: 0;
      margin: 0;

      a:hover {
        border-bottom: 1px solid #1779ba;
      }

      &:not(:first-child):after {
        content: ' | ';
      }
    }
  }

  .header-grid {
    width: 100%;
    height: 100vh;
    display: grid;
    grid-template-rows: 1fr 1fr 1fr;
    grid-template-columns: repeat(5, 1fr);
    grid-template-areas:
    "big-top big-top big-top small-top small-top"
    "small-middle small-middle big-middle big-middle big-middle"
    "big-bottom big-bottom big-bottom big-bottom big-bottom";
  }

  .search-grid:after {
    content: '';
    display: block;
    clear: both;
  }

  .grid-item {
    width: 20%;
  }

  .grid-item--width2 {
    width: 50%;
  }
</style>
