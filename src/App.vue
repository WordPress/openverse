<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<script>
import { FETCH_IMAGE_PROVIDERS } from '@/store/action-types';

export default {
  name: 'App',
  beforeMount() {
    this.$store.dispatch(FETCH_IMAGE_PROVIDERS);
  },
};
</script>

<style lang="scss">
@import './styles/app';

body {
  margin: 0;
}

#app {
  font-family: source sans pro,sans-serif !important;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>
