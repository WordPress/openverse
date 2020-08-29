<template>
  <HeroSection />
</template>

<script>
import { CLEAR_FILTERS } from '~/store-modules/mutation-types'

const HomePage = {
  name: 'home-page',
  fetch() {
    // clear filters on every client-side visit to the homepage
    console.log(this.$store.state.filters.licenseTypes)
    console.log('cleared filters!')
    this.$store.commit(CLEAR_FILTERS, {})
    console.log(this.$store.state.filters.licenseTypes)
  },
  fetchOnServer: false,
}

export default HomePage
</script>
