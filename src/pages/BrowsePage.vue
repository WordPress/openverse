<template>
  <div class="browse-page">
    <div class="search grid-x flexible">
      <div class="cell">
        <header-section :isHeaderFixed="true">
          <search-grid-form></search-grid-form>
        </header-section>
      </div>
      <div :class="{ 'cell search-grid-ctr': true }">
        <search-grid v-if="query.q"></search-grid>
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
import { FETCH_IMAGES } from '@/store/action-types';

const BrowsePage = {
  name: 'browse-page',
  components: {
    HeaderSection,
    SearchGridForm,
    SearchGrid,
    FooterSection,
  },
  data: () => ({
    isHeaderFixed: false,
  }),
  computed: {
    images() {
      return this.$store.state.images;
    },
    imagesCount() {
      return this.$store.state.imagesCount;
    },
    query() {
      return this.$store.state.query;
    },
    isFilterVisible() {
      return this.$store.state.isFilterVisible;
    },
  },
  methods: {
    getImages(params) {
      this.$store.dispatch(FETCH_IMAGES, params);
    },
  },
  created() {
    this.ticking = false;
    if (this.query.q) {
      this.getImages(this.query);
    }
  },
};

export default BrowsePage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>

<style lang="scss">
  .search-grid {
    margin: 165px 30px 60px 30px;


    /* Small only */
    @media screen and (max-width: 39.9375em) {
      margin: 165px 15px 30px 15px;
    }
  }

  .search-grid-ctr {
    background: #e9ebee;
    min-height: 600px;
    margin: 0;
    transition: margin .7s ease-in-out;
  }

  .search-grid-ctr__filter-visible {
    margin-top: 30px;
  }
</style>
