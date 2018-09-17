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

.feedback-tab {
  display: block;
  position: fixed;
  right: -20px;
  top: 50%;
  background: #049bce;
  transform: rotate(270deg);
  transform-origin: top;
  border-top: 5px solid #fff;
  border-left: 5px solid #fff;
  border-right: 5px solid #fff;
  border-radius: 20px 20px 0 0;
  box-shadow: 0 0 10px 0 rgba(0,0,0,.8);
  z-index: 1000;
  padding: .5rem 1rem;
  color: #fff;
  font-size: 20px;

  &:hover {
    color: white;
    text-decoration: underline;
  }

  @media screen and (max-width: 670px) {
    & {
      display: none;
    }
  }
}
</style>
