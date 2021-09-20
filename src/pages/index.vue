<template>
  <HeroSection />
</template>

<script>
import { CLEAR_FILTERS } from '~/constants/mutation-types'

const HomePage = {
  name: 'home-page',
  layout({ store }) {
    return store.state.nav.isEmbedded ? 'embedded' : 'default'
  },
  beforeMount() {
    this.$store.commit(CLEAR_FILTERS)
  },
}

export default HomePage
</script>
