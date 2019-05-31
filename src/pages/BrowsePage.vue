<template>
  <div class="browse-page">
    <div class="search grid-x flexible">
      <div class="cell">
        <header-section>
          <search-grid-form @onSearchFormSubmit="onSearchFormSubmit" />
        </header-section>
      </div>
      <div :class="{ 'cell search-grid-ctr': true }">
        <search-grid v-if="query.q"
                     :query="query"
                     @onLoadMoreImages="onLoadMoreImages"></search-grid>
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
import { SET_QUERY } from '@/store/mutation-types';

const BrowsePage = {
  name: 'browse-page',
  components: {
    HeaderSection,
    SearchGridForm,
    SearchGrid,
    FooterSection,
  },
  computed: {
    query() {
      return this.$store.state.query;
    },
  },
  methods: {
    getImages(params) {
      this.$store.dispatch(FETCH_IMAGES, params);
    },
    onLoadMoreImages(searchParams) {
      this.getImages(searchParams);
    },
    onSearchFormSubmit(searchParams) {
      this.$store.commit(SET_QUERY, searchParams);
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
    margin: 30px 30px 60px 30px;
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
