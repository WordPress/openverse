<template>
  <div class="app">
    <MigrationNotice v-show="isReferredFromCc" />
    <TranslationStatusBanner />
    <HeaderSection />
    <main class="embedded">
      <Nuxt />
    </main>
  </div>
</template>
<script>
import iframeHeight from '~/mixins/iframe-height'

import { NAV } from '~/constants/store-modules'

import { useContext } from '@nuxtjs/composition-api'
import TranslationStatusBanner from '~/components/TranslationStatusBanner.vue'

const embeddedPage = {
  name: 'embedded',
  components: { TranslationStatusBanner },
  layout: 'embedded',
  mixins: [iframeHeight],
  head() {
    return this.$nuxtI18nHead({ addSeoAttributes: true, addDirAttribute: true })
  },
  setup() {
    const { store } = useContext()
    const isReferredFromCc = store.state[NAV].isReferredFromCc

    return {
      isReferredFromCc,
    }
  },
}
export default embeddedPage
</script>
