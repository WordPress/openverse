<template>
  <HeroSection />
</template>

<script>
import { SEARCH } from '~/constants/store-modules'
import { CLEAR_FILTERS } from '~/constants/action-types'

const HomePage = {
  name: 'home-page',
  layout: 'default',
  beforeMount() {
    this.$store.dispatch(`${SEARCH}/${CLEAR_FILTERS}`)
  },
}

export default HomePage
</script>
