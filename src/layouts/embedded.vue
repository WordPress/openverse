<template>
  <div class="app">
    <HeaderSection />
    <main class="embedded">
      <Nuxt />
    </main>
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
