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
  font-family: 'Helvetica Neue', Helvetica, Roboto, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}
</style>
