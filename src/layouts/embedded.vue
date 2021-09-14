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

const defaultPage = {
  name: 'default',
  layout: 'default',
  head() {
    return this.$nuxtI18nHead({ addSeoAttributes: true })
  },
  computed: mapState(['isReferredFromCc']),
}
export default defaultPage
</script>
