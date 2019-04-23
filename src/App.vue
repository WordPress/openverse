<template>
  <div id="app">
    <router-view/>
  </div>
</template>
<script>
export default {
  name: 'App',
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
