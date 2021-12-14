<template>
  <VHeroSection />
</template>

<script>
import { SEARCH } from '~/constants/store-modules'
import { CLEAR_FILTERS } from '~/constants/action-types'

import VHeroSection from '~/components/VHeroSection.vue'

const HomePage = {
  name: 'home-page',
  layout: 'default',
  components: {
    VHeroSection,
  },
  beforeMount() {
    this.$store.dispatch(`${SEARCH}/${CLEAR_FILTERS}`)
  },
}

export default HomePage
</script>
