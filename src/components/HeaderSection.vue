<template>
  <header>
    <nav-section
      :showNavSearch="showNavSearch"
      :navSearchPlaceholder="navSearchPlaceholder"
    />
    <DonationBanner v-show="showDonate" @onDismiss="hideDonate" />
    <slot></slot>
  </header>
</template>

<script>
import NavSection from '@/components/NavSection'
import local from '@/utils/local'
import DonationBanner from './DonationBanner'

export default {
  name: 'header-section',
  components: {
    NavSection,
    DonationBanner,
  },
  props: ['showHero', 'showNavSearch', 'isHeaderFixed', 'navSearchPlaceholder'],
  data() {
    return {
      showDonate: !local.get('hide-location-banner') || true,
    }
  },
  methods: {
    hideDonate() {
      local.set('hide-location-banner', true)
      this.showDonate = false
    },
  },
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
