<template>
  <div class="grid-container full">
    <main class="not-found">
      <h1 v-if="error.statusCode === 404">
        {{ $t('not-found') }}
      </h1>
      <h1 v-else>An error occurred</h1>
    </main>
  </div>
</template>

<script>
const HomePage = {
  name: 'home-page',
  props: ['error'],
  layout: 'default',
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
