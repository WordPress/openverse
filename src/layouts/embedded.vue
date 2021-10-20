<template>
  <div class="app">
    <MigrationNotice v-show="isReferredFromCc" />
    <HeaderSection />
    <main class="embedded">
      <Nuxt />
    </main>
  </div>
</template>
<script>
import { mapState } from 'vuex'
import iframeHeight from '~/mixins/iframe-height'
import i18nSync from '~/mixins/i18n-sync'

const embeddedPage = {
  name: 'embedded',
  layout: 'embedded',
  mixins: [iframeHeight, i18nSync],
  head() {
    return this.$nuxtI18nHead({ addSeoAttributes: true, addDirAttribute: true })
  },
  computed: { ...mapState('nav', ['isReferredFromCc']) },
}
export default embeddedPage
</script>
