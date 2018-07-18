<template>
  <header class="header">
    <img src="../assets/cc-logo_large.png">
    <h1>{{ msg }}</h1>
  </Header>
</template>

<script>
export default {
  name: 'HeaderBar',
  data() {
    return {
      msg: 'Share, Collaborate, Remix, Reuse',
    };
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1, h2 {
  font-weight: normal;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
