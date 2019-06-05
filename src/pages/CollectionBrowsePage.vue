<template>
  <div class="browse-page">
    <div class="search grid-x flexible">
      <div class="cell">
        <header-section></header-section>
      </div>
      <div class="cell">
        <search-grid-form @onSearchFormSubmit="onSearchFormSubmit" />
      </div>
      <div :class="{ 'cell search-grid-ctr': true }">
        <search-grid v-if="query.provider"
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
import { FETCH_COLLECTION_IMAGES } from '@/store/action-types';
import { SET_COLLECTION_QUERY } from '@/store/mutation-types';

const CollectionBrowsePage = {
  name: 'collection-browse-page',
  props: ['provider'],
  components: {
    HeaderSection,
    SearchGridForm,
    SearchGrid,
    FooterSection,
  },
  computed: {
    query() {
      return {
        ...this.$store.state.query,
        provider: this.$props.provider,
      };
    },
  },
  methods: {
    getImages(params) {
      this.$store.dispatch(FETCH_COLLECTION_IMAGES, params);
    },
    onLoadMoreImages(searchParams) {
      this.getImages(searchParams);
    },
    onSearchFormSubmit(searchParams) {
      this.$store.commit(SET_COLLECTION_QUERY, {
        ...searchParams,
        provider: this.$props.provider,
      });
    },
  },
  created() {
    this.ticking = false;
    if (this.query.provider) {
      this.getImages(this.query);
    }
  },
};

export default CollectionBrowsePage;
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
