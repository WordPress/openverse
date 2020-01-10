<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<script>
import { FETCH_IMAGE_PROVIDERS } from '@/store/action-types';

export default {
  name: 'App',
  methods: {
    fetchProviders() {
      return this.$store.dispatch(FETCH_IMAGE_PROVIDERS);
    },
  },
  beforeMount() {
    if (!this.$store.state.imageProviders || !this.$store.state.imageProviders.length) {
      this.fetchProviders();
    }
  },
};
</script>

<style lang="scss">
@import './styles/app';

body {
  margin: 0;
}

#app {
  font-family: 'Source Sans Pro', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>
