<template>
  <div class="home-page grid-container full">
    <header-section></header-section>
    <hero-section></hero-section>
    <footer-section></footer-section>
  </div>
</template>

<script>
import HeaderSection from '@/components/HeaderSection'
import HeroSection from '@/components/HeroSection'
import FooterSection from '@/components/FooterSection'
import { CLEAR_FILTERS } from '../store/mutation-types'

const HomePage = {
  name: 'home-page',
  components: {
    HeaderSection,
    HeroSection,
    FooterSection,
  },
  mounted() {
    this.$store.commit(CLEAR_FILTERS, {
      provider: null,
      shouldNavigate: false,
    })
  },
}

export default HomePage
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
@import 'node_modules/bulma/sass/utilities/_all';

.home-page_body {
  /* Small only */
  @include mobile {
    margin: 60px 0 30px;
  }
}

.block {
  position: relative;
  height: 100%;
  width: 100%;
  max-height: 250px;
  overflow: hidden;
  border: 1px solid white;
  background: black;
  opacity: 0.8;
  transition: opacity 0.2s ease-out;
  cursor: pointer;

  &:hover {
    transition: opacity 0.2s ease-in;
    opacity: 1;
  }
}

.b1 {
  grid-area: big-top;
}

.b2 {
  grid-area: small-top;
}

.b3 {
  grid-area: small-middle;
}

.b4 {
  grid-area: big-middle;
}

.footer {
  position: fixed;

  /* Small only */
  @include mobile {
    position: relative;
  }
}
</style>
