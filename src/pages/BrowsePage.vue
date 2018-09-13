<template>
  <div class="browse-page">
    <div class="search grid-x flexible">
      <div class="cell">
        <header-section :isHeaderFixed="isHeaderFixed">
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
        <share-list></share-list>
      </div>
    </div>
    <footer-section></footer-section>
  </div>
</template>

<script>
import FooterSection from '@/components/FooterSection';
import HeaderSection from '@/components/HeaderSection';
import SearchGrid from '@/components/SearchGrid';
import SearchGridForm from '@/components/SearchGridForm';
import ShareList from '@/components/ShareList';
import { FETCH_IMAGES } from '@/store/action-types';
import { SET_GRID_FILTER, SET_IMAGES } from '@/store/mutation-types';


const BrowsePage = {
  name: 'browse-page',
  components: {
    HeaderSection,
    SearchGridForm,
    ShareList,
    SearchGrid,
    FooterSection,
  },
  data: () => ({
    isHeaderFixed: false,
    isVisible: false,
  }),
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
    onScroll() {
      const scrollYPosition = window.scrollY;

      if (!this.ticking) {
        window.requestAnimationFrame(() => {
          if (scrollYPosition > 134) {
            this.isHeaderFixed = true;
          } else {
            this.isHeaderFixed = false;
          }
          this.ticking = false;
        });
        this.ticking = true;
      }
    },
  },
  created() {
    const queryParam = this.$route.query.q;

    this.$store.commit(SET_IMAGES,
      { images: [] },
    );

    if (queryParam) {
      this.getImages({ q: queryParam, filter: this.filter });
    }

    this.unsubscribe = this.$store.subscribe((mutation) => {
      if (mutation.type === SET_GRID_FILTER) {
        this.getImages({ q: this.query, ...mutation.payload.filter });
      }
    });

    this.ticking = false;
    window.addEventListener('scroll', this.onScroll);
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
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>

<style lang="scss">
  .search-grid {
    margin: 30px 30px 60px 30px;
    min-height: 600px;

    /* Small only */
    @media screen and (max-width: 39.9375em) {
      margin: 30px 15px 30px 15px;
    }
  }
</style>
