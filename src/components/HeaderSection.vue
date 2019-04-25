<template>
  <header :class="header">
    <nav-section :showNavSearch="showNavSearch"></nav-section>
     <slot></slot>
  </header>
</template>

<script>
import NavSection from '@/components/NavSection';

export default {
  name: 'header-section',
  components: {
    NavSection,
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
    width: 100%;
    max-width: 100%;

    &__fixed {
      position: fixed;
      top: 0;
      left: 0;
      animation-duration: .3s;
      animation-name: fadeIn;
    }
  }

  .header nav {
    z-index: 10;
  }
</style>
