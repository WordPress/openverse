<template>
  <div class="share-list-page">
    <div class="search grid-x flexible">
      <div class="cell">
        <header-section>
          <search-form></search-form>
        </header-section>
      </div>
      <div class="cell share-list">
        <div class="add-people-header">
          <h5 class="header-title">
            Lists
          </h5>
          <div class="small-12 medium-6 columns share-list_items">
            <div v-for="(image, index) in images"
                 :class="{ 'search-grid_item': true, 'search-grid_ctr__active': image.isActive }"
                 :key="index">
              <img class="search-grid_image" :src="image.url">
            </div>
          </div>
        </div>
      </div>
    </div>
    <footer-section></footer-section>
  </div>
</template>

<script>
import HeaderSection from '@/components/HeaderSection';
import FooterSection from '@/components/FooterSection';
import SearchGridForm from '@/components/SearchGridForm';
import { FETCH_LIST } from '@/store/action-types';

const ShareListPage = {
  name: 'share-list-page',
  components: {
    HeaderSection,
    SearchGridForm,
    FooterSection,
  },
  props: {
    id: null,
  },
  computed: {
    images() {
      return this.$store.state.images;
    },
  },
  created() {
    this.$store.dispatch(FETCH_LIST, { id: this.id });
  },
};

export default ShareListPage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss">
  .share-list {
    margin: 30px;
    min-height: 450px;
  }

</style>
