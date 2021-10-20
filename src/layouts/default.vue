<template>
  <div class="app">
    <HeaderSection :is-embedded="false" />
    <main>
      <Nuxt />
    </main>
    <FooterSection />
  </div>
</template>
<script>
const defaultPage = {
  name: 'default',
  layout: 'default',
  head() {
    return this.$nuxtI18nHead({ addSeoAttributes: true, addDirAttribute: true })
  },
}
export default defaultPage
</script>
