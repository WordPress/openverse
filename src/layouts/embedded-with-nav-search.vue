<template>
  <div class="app">
    <MigrationNotice v-show="isReferredFromCc" />
    <HeaderSection :show-nav-search="true" />
    <main class="embedded">
      <Nuxt />
    </main>
  </div>
</template>
<script>
import { mapState } from 'vuex'
import iframeHeight from '~/mixins/iframe-height'
import i18nSync from '~/mixins/i18n-sync'

const embeddedWithNavSearch = {
  name: 'embedded-with-nav-search',
  layout: 'embedded-with-nav-search',
  mixins: [iframeHeight, i18nSync],
  head() {
    return this.$nuxtI18nHead({ addSeoAttributes: true, addDirAttribute: true })
  },
  computed: { ...mapState('nav', ['isReferredFromCc']) },
}
export default embeddedWithNavSearch
</script>
