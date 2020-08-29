<template>
  <div class="app">
    <HeaderSection :show-nav-search="true" />
    <main role="main">
      <Nuxt />
    </main>
    <FooterSection />
  </div>
</template>

<style lang="scss">
@import '~/styles/global.scss';
</style>
