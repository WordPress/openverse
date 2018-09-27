<template>
  <nav class="nav grid-x grid-padding-x">
    <div class="cell small-12 medium-12 large-6">
      <a href="https://creativecommons.org/">
        <img class="nav_logo" src="../assets/cc-logo_white.png">
      </a>
      <div class="menu_ctr">
        <ul class="menu">
          <li class="home"><a href="./">Home</a></li>
          <li class="list-option">
            <a href='/lists'>
              Lists
              <transition name="slide-fade" mode="out-in">
                <span class="badge alert" v-if="listsCount"
                  :key="listsCount">{{ listsCount }}</span>
              </transition>
            </a>
          </li>
          <li><a href="./about">About</a></li>
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
import { FETCH_LISTS } from '@/store/action-types';

export default {
  props: ['showNavSearch', 'fixedNav'],
  name: 'nav-section',
  data: () => ({ form: { searchTerm: '' } }),
  computed: {
    listsCount() {
      return this.$store.state.shareLists.length;
    },
  },
  mounted() {
    this.$store.dispatch(FETCH_LISTS);
  },
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
  background-color: #373737;
}

.nav_logo {
  margin: 15px 0 15px 0px;
  height: 30px;
}

.hero_search-form {
  margin: 0 15px;

  /* Large and up */
  @media screen and (min-width: 64em) {
    float: right;
  }
}

.menu_ctr {
  display: inline-block;
  margin-left: 30px;

  /* Small only */
  @media screen and (max-width: 39.9375em) {
    margin-left: 0 !important;
  }
}

.menu a {
  color: #fefefe;
  font-weight: 500;
  padding: 0.7rem 1rem;
  border: 1px solid transparent;
  border-radius: 2px;
  transition: all 0.3s ease;

  &:hover {
    border-color: rgba(255, 255, 255, 0.3);
  }

  .badge {
    line-height: 1.5em;
    position: absolute;
    top: 1px;
    right: 1px;
  }
}

.list-option {
  position: relative;
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
