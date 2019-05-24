<template>
  <div class="collections-page grid-container full">
  <header-section></header-section>
  <div class="collections-page_body">
        <h1>Browser our providers' collections</h1>
    </div>
    <footer-section></footer-section>
  </div>
</template>

<script>
import HeaderSection from '@/components/HeaderSection';
import FooterSection from '@/components/FooterSection';

const CollectionsPage = {
  name: 'collections-page',
  components: {
    HeaderSection,
    FooterSection,
  },
};

export default CollectionsPage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>

</style>
