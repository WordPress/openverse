<template>
  <HeroSection />
</template>

<script>
import { FILTER } from '~/constants/store-modules'
import { CLEAR_FILTERS } from '~/constants/mutation-types'

const HomePage = {
  name: 'home-page',
  layout({ store }) {
    return store.state.nav.isEmbedded ? 'embedded' : 'default'
  },
  beforeMount() {
    this.$store.dispatch(`${FILTER}/${CLEAR_FILTERS}`)
  },
}

export default HomePage
</script>
