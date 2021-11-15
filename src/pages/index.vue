<template>
  <HeroSection />
</template>

<script>
import { SEARCH } from '~/constants/store-modules'
import { CLEAR_FILTERS } from '~/constants/mutation-types'

const HomePage = {
  name: 'home-page',
  layout({ store }) {
    return store.state.nav.isEmbedded ? 'embedded' : 'default'
  },
  beforeMount() {
    this.$store.dispatch(`${SEARCH}/${CLEAR_FILTERS}`)
  },
}

export default HomePage
</script>
