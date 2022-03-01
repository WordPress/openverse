<template>
  <div>
    <VMigrationNotice v-show="isReferredFromCc" />
    <VTranslationStatusBanner />
    <Nuxt />
  </div>
</template>

<script>
import { defineComponent, useStore } from '@nuxtjs/composition-api'

import iframeHeight from '~/mixins/iframe-height'

import { NAV } from '~/constants/store-modules'

import VTranslationStatusBanner from '~/components/VTranslationStatusBanner.vue'

import VMigrationNotice from '~/components/VMigrationNotice.vue'

export default defineComponent({
  name: 'Blank',
  components: { VMigrationNotice, VTranslationStatusBanner },
  mixins: [iframeHeight],
  setup() {
    const store = useStore()
    const isReferredFromCc = store.state[NAV].isReferredFromCc
    return { isReferredFromCc }
  },
  head() {
    return this.$nuxtI18nHead({ addSeoAttributes: true, addDirAttribute: true })
  },
})
</script>
