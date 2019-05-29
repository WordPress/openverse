<template>
  <div>
    <header-section></header-section>
    <div class="collections-page grid-container full">
      <h1>Browser our providers' collections</h1>
      <div class="providers-list grid-x">
        <collection-item class="card provider-card cell small"
                         v-for="(provider, index) in providers"
                         :key="index"
                         :provider="provider" />
      </div>
    </div>
    <footer-section></footer-section>
  </div>
</template>

<script>
import CollectionItem from '@/components/CollectionItem';
import HeaderSection from '@/components/HeaderSection';
import FooterSection from '@/components/FooterSection';

const CollectionsPage = {
  name: 'collections-page',
  components: {
    HeaderSection,
    FooterSection,
    CollectionItem,
  },
  computed: {
    providers() {
      return this.$store.state.imageProviders;
    },
  },
};

export default CollectionsPage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  h1 {
    margin-bottom: .44117647em;
    font-size: 2.125em;
    font-weight: normal;
    letter-spacing: initial;
    line-height: 1.25;
    text-transform: initial;
  }

  .collections-page {
    margin: 45px !important;
  }
</style>
