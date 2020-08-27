<template>
  <header>
    <nav-section
      :showNavSearch="showNavSearch"
      :navSearchPlaceholder="navSearchPlaceholder"
    />
    <slot />
  </header>
</template>

<script>
import NavSection from './NavSection'

export default {
  name: 'header-section',
  components: {
    NavSection,
  },
  props: ['showHero', 'showNavSearch', 'isHeaderFixed', 'navSearchPlaceholder'],
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss">
.header {
  position: relative;
  z-index: 200;
  width: 100%;
  max-width: 100%;
}

.header nav {
  z-index: 10;
}
</style>
