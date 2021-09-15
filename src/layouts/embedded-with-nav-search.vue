<template>
  <div class="app">
    <HeaderSection :show-nav-search="true" />
    <main class="embedded">
      <Nuxt />
    </main>
  </div>
</template>
<script>
import iframeHeight from '~/mixins/iframe-height'
import i18nSync from '~/mixins/i18n-sync'

const embeddedWithNavSearch = {
  name: 'embedded-with-nav-search',
  mixins: [iframeHeight, i18nSync],
  layout: 'embedded-with-nav-search',
  head() {
    return this.$nuxtI18nHead({ addSeoAttributes: true })
  },
}
export default embeddedWithNavSearch
</script>
