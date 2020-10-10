<template>
  <HeroSection />
</template>

<script>
import { CLEAR_FILTERS } from '~/store-modules/mutation-types'

const HomePage = {
  name: 'home-page',
  beforeMount() {
    this.$store.commit(CLEAR_FILTERS)
  },
}

export default HomePage
</script>
