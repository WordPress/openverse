<template>
  <Nuxt />
</template>

<script>
import { defineComponent } from '@nuxtjs/composition-api'
import iframeHeight from '~/mixins/iframe-height'

export default defineComponent({
  name: 'Blank',
  mixins: [iframeHeight],
  head() {
    return this.$nuxtI18nHead({ addSeoAttributes: true, addDirAttribute: true })
  },
})
</script>
