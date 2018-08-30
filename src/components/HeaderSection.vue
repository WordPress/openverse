<template>
  <header :class="{ header: true, 'header__fixed': isHeaderFixed }">
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
  props: ['showHero', 'showNavSearch', 'isHeaderFixed'],
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss">
  @import '../../node_modules/foundation-sites/scss/foundation';

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; position: fixed; }
  }

  .header {
    position: relative;
    z-index: 200;


    &__fixed {
      position: fixed;
      top: 0;
      left: 0;
      animation-duration: 1s;
      animation-name: fadeIn;

      nav {
        background: #000 !important;
      }
    }
  }

  .header nav {
    z-index: 10;
  }
</style>
