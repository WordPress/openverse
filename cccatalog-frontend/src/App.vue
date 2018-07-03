<template>
  <div id="navbar">
    <Navbar msg="Creative Commons Catalog"/>
  </div>
</template>

<script>
import Navbar from './components/Navbar.vue'

export default {
  name: 'app',
  components: {
    Navbar
  }
}
</script>

<style>
#navbar {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
/* Override user agent CSS*/
body {
  margin-top:0px;
  margin-right: 0px;
  margin-bottom:0px;
  margin-left: 0px;
}
</style>
