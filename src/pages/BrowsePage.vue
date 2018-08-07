<template>
  <div class="browse-page">
    <div class="search grid-x flexible">
      <div class="cell">
        <header-section>
          <search-form :query="query"></search-form>
        </header-section>
      </div>
      <div class="cell">
        <search-grid
          :imagesCount="imagesCount"
          :images="images"
          :query="query">
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
import SearchForm from '@/components/SearchForm';
import SearchGrid from '@/components/SearchGrid';
import ShareBar from '@/components/ShareBar';
import { FETCH_IMAGES } from '@/store/action-types';

const BrowsePage = {
  name: 'browse-page',
  components: {
    HeaderSection,
    SearchForm,
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
  },
  created() {
    const queryParam = this.$route.query.q;

    if (queryParam) {
      this.$store.dispatch(FETCH_IMAGES, { q: queryParam });
    }
  },
};

export default BrowsePage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss"></style>
