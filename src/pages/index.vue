<template>
  <HeroSection />
</template>

<script>
import { CLEAR_FILTERS } from '~/store-modules/mutation-types'
import iframeHeight from '~/mixins/iframe-height'
import i18nSync from '~/mixins/i18n-sync'

const HomePage = {
  name: 'home-page',
  mixins: [iframeHeight, i18nSync],
  layout({ store }) {
    return store.state.isEmbedded ? 'embedded' : 'default'
  },
  beforeMount() {
    this.$store.commit(CLEAR_FILTERS)
  },
}

export default HomePage
</script>
