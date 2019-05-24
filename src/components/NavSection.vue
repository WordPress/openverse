<template>
  <nav class="nav grid-x grid-padding-x">
    <div class="cell small-12 medium-12 large-6">
      <a class="nav_logo" href="/">
        <img src="../assets/cc-search-logo-white.png">
      </a>
      <div class="menu_ctr">
        <ul class="menu">
          <li><a href="/collections">Collections</a></li>
          <li><a href="/about">About</a></li>
          <li><a href="/feedback">Feedback</a></li>
        </ul>
      </div>
    </div>
    <div class="cell small-12 medium-12 large-6 align-center nav_search"
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
import { SET_QUERY } from '@/store/mutation-types';

export default {
  props: ['showNavSearch', 'fixedNav'],
  name: 'nav-section',
  data: () => ({ form: { searchTerm: '' } }),
  methods: {
    onSubmit() {
      this.$store.commit(SET_QUERY, { query: { q: this.form.searchTerm }, shouldNavigate: true });
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
.nav {
  position: relative;
  width: 100%;
  background-image: linear-gradient(90deg, #34baec, #5fd1fc, #34baec);
  height: 3.9em;
  border-bottom: 1px solid rgba(0,0,0,0.25);
}
.nav_logo > img {
  margin: 0px 0 9px 0;
  height: 42px;
  padding-right: 11px;
}
.hero_search-form {
  margin: 0 15px;
  /* Large and up */
  @media screen and (min-width: 64em) {
    float: right;
  }
  /* Small only */
  @media screen and (max-width: 39.9375em) {
    display: none;
  }
}
.menu_ctr {
  display: inline-block;
  margin-left: 10px;
  /* Small only */
  @media screen and (max-width: 39.9375em) {
    margin-left: 0 !important;
  }
}

.menu a {
  color: rgb(255, 255, 255);
  font-size: 1.6em;
  font-weight: 700;
  line-height: 1em;
  margin-top: 0.5rem;
  border-left: 1px solid white;
  border-radius: 2px;
  &:hover {
    background: #1e96c2;
  }

  /* Small only */
  @media screen and (max-width: 380px) {
    padding: 0.7rem .7rem;
    font-size: 1.2em;
    &:hover {
      border-bottom: none;
    }
  }

  @media screen and (max-width: 320px) {
    font-size: .93em;
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
    border: 1px solid rgba(36, 36, 36, 0.5);;
    box-shadow: none;
    &:focus {
      border-color: rgb(255, 255, 255);
    }

    &::placeholder {
      color: #1c1c1c;
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
      background: url('../assets/search-icon_black.svg') center center no-repeat;
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
.slide-fade-enter-active {
  transition: all .3s ease;
}
.slide-fade-leave-active {
  transition: all .8s cubic-bezier(1.0, 0.5, 0.8, 1.0);
}
.slide-fade-enter, .slide-fade-leave-to {
  transform: translateX(10px);
  opacity: 0;
}
</style>
