<template>
  <HeroSection />
</template>

<script>
import { CLEAR_FILTERS } from '~/store-modules/mutation-types'
import iframeHeight from '~/mixins/iframeHeight'

const HomePage = {
  name: 'home-page',
  mixins: [iframeHeight],
  layout({ store }) {
    return store.state.isEmbedded ? 'embedded' : 'default'
  },
  beforeMount() {
    this.$store.commit(CLEAR_FILTERS)
  },
}

export default HomePage
</script>
