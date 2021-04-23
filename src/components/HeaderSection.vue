<template>
  <header>
    <NavSection :key="$route.path" :show-nav-search="showNavSearch" />
    <DonationBanner @onDismiss="hideDonate" />
    <slot />
  </header>
</template>

<script>
import NavSection from '@/components/NavSection'
import local from '@/utils/local'
import DonationBanner from './DonationBanner'

export default {
  name: 'HeaderSection',
  components: {
    NavSection,
    DonationBanner,
  },
  props: { showNavSearch: { type: Boolean, default: false } },
  data() {
    return {
      showDonate: !local.get('hide-donation-banner'),
    }
  },
  methods: {
    hideDonate() {
      local.set('hide-donation-banner', true)
      this.showDonate = false
    },
  },
}
</script>
