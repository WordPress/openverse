<template>
  <div class="app">
    <HeaderSection :show-nav-search="true" :is-embedded="false" />
    <main>
      <Nuxt />
    </main>
    <FooterSection />
  </div>
</template>
<script>
const withNavSearch = {
  name: 'with-nav-search',
  layout: 'with-nav-search',
  head() {
    return this.$nuxtI18nHead({ addSeoAttributes: true })
  },
}
export default withNavSearch
</script>
