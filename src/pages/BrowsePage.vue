<template>
  <div class="browse-page">
    <header-section></header-section>
    <div class="search grid-x flexible">
      <div class="cell">
        <search-form :query="query"></search-form>
      </div>
      <div class="cell">
        <search-grid :data="images"></search-grid>
      </div>
    </div>
    <footer-section></footer-section>
  </div>
</template>

<script>
import FooterSection from '@/components/FooterSection';
import HeaderSection from '@/components/HeaderSection';
import SearchForm from '@/components/SearchForm';
import SearchGrid from '@/components/SearchGrid';
import { FETCH_IMAGES } from '@/store/action-types';

const BrowsePage = {
  name: 'browse-page',
  components: {
    HeaderSection,
    SearchForm,
    SearchGrid,
    FooterSection,
  },
  computed: {
    images() {
      return this.$store.state.images;
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
<style lang="scss">
.search {
  padding: 0;
  box-shadow: 0;
  border-bottom: 1px solid #e6e6e6;
}

.search-form {
  width: 100% !important;
  margin: 0 !important;
}

.search_input {
  border-radius: 0 !important;
  color: #000 !important;
}
</style>
