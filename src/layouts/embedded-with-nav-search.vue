<template>
  <div class="app">
    <HeaderSection :show-nav-search="true" />
    <main class="embedded">
      <Nuxt />
    </main>
  </div>
</template>
<script>
const embeddedWithNavSearch = {
  name: 'embedded-with-nav-search',
  layout: 'embedded-with-nav-search',
  head() {
    return this.$nuxtI18nHead({ addSeoAttributes: true })
  },
}
export default embeddedWithNavSearch
</script>
