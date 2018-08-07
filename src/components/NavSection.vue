<template>
  <nav class="nav">
    <a href="/">
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
.nav {
  position: relative;
  width: 100%;
  height: 60px;
  background: rgba(0,0,0,0.8);
}

.nav_logo {
  padding-left: 30px;
  height: 30px;
  float: left;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
}
</style>
