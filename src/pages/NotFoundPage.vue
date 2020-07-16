<template>
  <div class="grid-container full">
    <header-section></header-section>
    <main class="not-found">
      {{ $t('not-found') }}
    </main>
    <footer-section></footer-section>
  </div>
</template>

<script>
import HeaderSection from '@/components/HeaderSection'
import FooterSection from '@/components/FooterSection'

const HomePage = {
  name: 'home-page',
  components: {
    HeaderSection,
    FooterSection,
  },
}

export default HomePage
</script>

<style lang="scss" scoped>
.not-found {
  height: 71vh;
  text-align: center;
  font-size: 2em;
  padding-top: 10vh;
}
</style>
