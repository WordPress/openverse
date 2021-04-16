<template>
  <div class="app">
    <HeaderSection />
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
    return this.$nuxtI18nHead({ addSeoAttributes: true })
  },
}
export default defaultPage
</script>
