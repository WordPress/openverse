<template>
  <header>
    <NavSection :key="$route.path" :show-nav-search="showNavSearch" />
    <div
      v-show="showDonate"
      :class="{
        'padding-bottom-bigger': needsPadding,
      }"
    >
      <DonationBanner @onDismiss="hideDonate" />
    </div>
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
      showDonate: !local.get('hide-location-banner'),
    }
  },
  computed: {
    // Only pad the donation banner when the current route requires it
    needsPadding() {
      return (
        !this.$route.path.startsWith('/photos') &&
        !(this.$route.path === '/search')
      )
    },
  },
  methods: {
    hideDonate() {
      local.set('hide-location-banner', true)
      this.showDonate = false
    },
  },
}
</script>
