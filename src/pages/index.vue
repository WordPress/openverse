<template>
  <HeroSection />
</template>

<script>
import { CLEAR_FILTERS } from '~/store-modules/mutation-types'
import abTests from '~/abTests'

const HomePage = {
  name: 'home-page',
  beforeMount() {
    this.$store.commit(CLEAR_FILTERS)
    abTests(this.$store)
  },
}

export default HomePage
</script>
