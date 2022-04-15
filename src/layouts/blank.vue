<template>
  <div>
    <VMigrationNotice />
    <VTranslationStatusBanner />
    <Nuxt />
  </div>
</template>

<script>
import { defineComponent } from '@nuxtjs/composition-api'

import VTranslationStatusBanner from '~/components/VTranslationStatusBanner.vue'
import VMigrationNotice from '~/components/VMigrationNotice.vue'

export default defineComponent({
  name: 'BlankLayout',
  components: { VMigrationNotice, VTranslationStatusBanner },
  head() {
    return this.$nuxtI18nHead({ addSeoAttributes: true, addDirAttribute: true })
  },
})
</script>
