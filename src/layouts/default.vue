<template>
  <div class="app">
    <HeaderSection />
    <main role="main">
      <Nuxt />
    </main>
    <FooterSection />
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: grid;
  grid-template-rows: auto 1fr auto;
}
</style>

<style lang="scss">
@import '@creativecommons/vocabulary/scss/vocabulary.scss';

body {
  margin: 0;
  font-family: 'Source Sans Pro', sans-serif;
  font-display: swap;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #333333;
}

.full-height-sticky {
  @include desktop {
    z-index: 20;
    height: 100vh;
    position: sticky;
    top: 0;
  }
}

// override global header styles for now
.cc-global-header .container {
  max-width: 100%;
}
</style>
