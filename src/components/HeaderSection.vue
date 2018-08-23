<template>
  <header class="header">
    <nav-section :showNavSearch="showNavSearch"></nav-section>
     <slot></slot>
    <hero-section v-if="showHero === 'true'"></hero-section>
  </header>
</template>

<script>
import NavSection from '@/components/NavSection';
import HeroSection from '@/components/HeroSection';

export default {
  name: 'header-section',
  components: {
    NavSection,
    HeroSection,
  },
  props: ['showHero', 'showNavSearch', 'fixedNav'],
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss">
  @import '../../node_modules/foundation-sites/scss/foundation';

  .header {
    position: relative;
  }

  .header nav {
    z-index: 10;
  }
</style>
