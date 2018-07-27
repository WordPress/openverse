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
  <div class="search-grid" ref="gridContainer">
    <div class="header-grid">
      <div id="b1" class="block"></div>
      <div id="b2" class="block"></div>
      <div id="b3" class="block"></div>
      <div id="b4" class="block"></div>
      <div class="bottom-block">
        <div id="b5" class="block"></div>
        <div id="b6" class="block"></div>
        <div id="b7" class="block"></div>
      </div>
    </div>
  </div>
</section>
</template>

<script>
import MasonryLayout from 'masonry-layout';

export default {
  name: 'search-grid',
  data: () => ({
    tags: [
      {
        tagName: 'City',
        tagImageSrc: require('@/assets/london-night_medium.jpg'), // eslint-disable-line global-require
      }, {
        tagName: 'Sunset',
        tagImageSrc: require('@/assets/london-night_medium.jpg'), // eslint-disable-line global-require
      }, {
        tagName: 'City',
        tagImageSrc: require('@/assets/london-night_medium.jpg'), // eslint-disable-line global-require
      }, {
        tagName: 'City',
        tagImageSrc: require('@/assets/london-night_medium.jpg'), // eslint-disable-line global-require
      },
    ],
  }),
  methods: {
    addData(data, options = {}) {
      if (options.render) {
        this.grid.render();
      }
    },
  },
  mounted() {
    this.grid = new MasonryLayout(this.$refs.grid, { // eslint-disable-line no-new
      itemSelector: '.grid-container',
      columnWidth: 200,
    });
  },
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  .search-grid {
    margin: 30px 0 60px 0;
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

  .block {
    height: 100%;
    width: 100%;
    border: 1px solid white;
    background: black;
    opacity: 0.8;
    transition: opacity 0.2s ease-out;

    &:hover {
      transition: opacity 0.2s ease-in;
      opacity: 1;

    }
  }

  #b1 {
    grid-area: big-top;

  }

  #b2 {
    grid-area :small-top;
  }

  #b3 {
    grid-area: small-middle;
  }

  #b4 {
    grid-area: big-middle;
  }

  .bottom-block {
    grid-area: big-bottom;
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;

  }

</style>
