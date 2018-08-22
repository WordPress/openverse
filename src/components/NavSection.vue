<template>
  <nav class="nav grid-x grid-padding-x">
    <div class="cell small-6 medium-12 large-6">
      <a href="/">
        <img class="nav_logo" src="../assets/cc-logo_white.png">
      </a>
    </div>
    <div class="cell small-6 medium-12 large-6 align-center nav_search"
         v-if="showNavSearch ==='true'">
      <form class="hero_search-form"
            role="search"
            method="post"
            v-on:submit.prevent="onSubmit">
        <div class="input-group input-group-rounded">
          <input class="input-group-field"
                 type="search"
                 placeholder="Search the commons..."
                 v-model.lazy="form.searchTerm">
          <div class="input-group-button">
            <button type="submit" class="button secondary" value="Search"></button>
          </div>
        </div>
      </form>
    </div>
  </nav>
</template>

<script>
export default {
  props: ['showNavSearch', 'fixedNav'],
  name: 'nav-section',
  data: () => ({ form: { searchTerm: '' } }),
  methods: {
    onSubmit() {
      this.$router.push({ path: '../search', query: { q: this.form.searchTerm } });
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
.nav {
  position: relative;
  width: 100%;
  background: rgba(0,0,0,0.8);
}

.nav_logo {
  margin: 15px 0 15px 15px;
  height: 30px;
}

.hero_search-form {
  margin: 0 15px;

  /* Large and up */
  @media screen and (min-width: 64em) {
    float: right;
  }
}

.input-group-rounded {
  margin: 9px 0;
  width: 400px;
  max-width: 100%;

  .input-group-field {
    border-radius: 3px;
    padding-left: 1rem;
    background: transparent;
    color: #fff;
    border: 1px solid rgba(255, 255, 255, .1);
    box-shadow: none;

    &:focus {
      border-color: rgba(213, 18, 188, .5);
    }
  }

  .input-group-button .button {
    border-radius: 3px;
    font-size: 0.8rem;
    height: 100%;
    position: relative;
    left: calc( -100% - 10px );
    background: none;

    &:after {
      content: '';
      background: url('../assets/search-icon.svg') center center no-repeat;
      background-size: 20px;
      top: 0;
      left: 0;
      bottom: 0;
      right: 0;
      position: absolute;
      z-index: 10;
      opacity: .2;
    }
  }
}

</style>
