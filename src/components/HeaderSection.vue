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
import abTests from '~/abTests'

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
  computed: {
    // Only pad the donation banner when the current route requires it
    needsPadding() {
      return (
        !this.$route.path.startsWith('/photos') &&
        !(this.$route.path === '/search')
      )
    },
  },
  /**
   * Note: this isn't the ideal place to do this, but we need this to run globally,
   * client-side, on any initial page visit,and the header is included on every
   * page so it's an okay place to do it.
   */
  beforeMount() {
    abTests(this.$store)
  },
  methods: {
    hideDonate() {
      local.set('hide-donation-banner', true)
      this.showDonate = false
    },
  },
}
</script>
