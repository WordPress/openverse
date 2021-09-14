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

const embeddedWithNavSearch = {
  name: 'embedded-with-nav-search',
  layout: 'embedded-with-nav-search',
  head() {
    return this.$nuxtI18nHead({ addSeoAttributes: true })
  },
  computed: mapState(['isReferredFromCc']),
}
export default embeddedWithNavSearch
</script>
