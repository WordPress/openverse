<template>
  <HeroSection />
</template>

<script>
import { CLEAR_FILTERS } from '~/store-modules/mutation-types'

const HomePage = {
  name: 'home-page',
  fetch() {
    // clear filters on every client-side visit to the homepage
    this.$store.commit(CLEAR_FILTERS, { provider: null })
  },
  fetchOnServer: false,
}

export default HomePage
</script>
