<template>
  <header>
    <nav-section
      :showNavSearch="showNavSearch"
      :navSearchPlaceholder="navSearchPlaceholder"
    />
    <DonationBanner />
    <slot></slot>
  </header>
</template>

<script>
import NavSection from '@/components/NavSection'
import DonationBanner from './Banner'

export default {
  name: 'header-section',
  components: {
    NavSection,
    DonationBanner,
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
