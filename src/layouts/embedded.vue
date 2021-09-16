<template>
  <div class="app">
    <HeaderSection />
    <main class="embedded">
      <Nuxt />
    </main>
  </div>
</template>
<script>
import iframeHeight from '~/mixins/iframe-height'
import i18nSync from '~/mixins/i18n-sync'

const embeddedPage = {
  name: 'embedded',
  mixins: [iframeHeight, i18nSync],
  layout: 'embedded',
  head() {
    return this.$nuxtI18nHead({ addSeoAttributes: true })
  },
}
export default embeddedPage
</script>
