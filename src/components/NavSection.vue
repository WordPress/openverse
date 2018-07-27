<template>
  <nav class="nav">
    <a href=".">
      <img class="nav_logo" src="../assets/cc-logo_white.png">
    </a>
  </nav>
</template>

<script>
export default {
  name: 'nav-section',
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
nav {
  height: 0px;
  width: 100%;
  position: absolute;
  left: 0;
  background: transparent;
}

.nav_logo {
  padding-left: 30px;
  padding-top: 30px;
  height: 70px;
  float: left;
  fill: #fff;
}
</style>
