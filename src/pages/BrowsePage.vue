<template>
  <div class="browse-page">
    <div class="search grid-x flexible">
      <div class="cell">
        <header-section>
          <search-grid-form :query="query"></search-grid-form>
        </header-section>
      </div>
      <div class="cell">
        <search-grid
          :imagesCount="imagesCount"
          :images="images"
          :query="query"
          :filter="filter">
        </search-grid>
        <share-bar></share-bar>
      </div>
    </div>
    <footer-section></footer-section>
  </div>
</template>

<script>
import HeaderSection from '@/components/HeaderSection';
import FooterSection from '@/components/FooterSection';
import SearchGridForm from '@/components/SearchGridForm';
import SearchGrid from '@/components/SearchGrid';
import ShareBar from '@/components/ShareBar';
import { FETCH_IMAGES } from '@/store/action-types';
import { SET_GRID_FILTER } from '@/store/mutation-types';

const BrowsePage = {
  name: 'browse-page',
  components: {
    HeaderSection,
    SearchGridForm,
    ShareBar,
    SearchGrid,
    FooterSection,
  },
  computed: {
    images() {
      return this.$store.state.images;
    },
    imagesCount() {
      return this.$store.state.imagesCount;
    },
    query() {
      return this.$store.state.query.q;
    },
    filter() {
      return this.$store.state.query.filter;
    },
  },
  methods: {
    getImages(params) {
      this.$store.dispatch(FETCH_IMAGES, params);
    },
  },
  created() {
    const queryParam = this.$route.query.q;

    if (queryParam) {
      this.getImages({ q: queryParam, filter: this.filter });
    }

    this.unsubscribe = this.$store.subscribe((mutation) => {
      if (mutation.type === SET_GRID_FILTER) {
        this.getImages({ q: this.query, ...mutation.payload.filter });
      }
    });
  },
  beforeDestroy() {
    this.unsubscribe();
  },
  beforeRouteUpdate(to, from, next) {
    this.getImages({ q: to.query.q, filter: this.filter });
    next();
  },
};

export default BrowsePage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss">
  .search-grid {
    margin: 30px 30px 60px 30px;
    min-height: 600px;
  }
</style>
