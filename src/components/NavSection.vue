<template>
  <nav class="navbar small">
    <div class="navbar-brand">
      <a class="logo" href="/">
        <img alt="Logo" src="../assets/cc-search-logo-black.png">
      </a>
      <a role="button" class="navbar-burger" aria-label="menu" aria-expanded="false">
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
      </a>
    </div>
    <div class="navbar-menu">
      <div class="margin-left-big"  v-if="showNavSearch ==='true'">
        <form class="hero_search-form"
              role="search"
              method="post"
              v-on:submit.prevent="onSubmit">
          <input class="input"
                type="search"
                :placeholder="navSearchPlaceholder"
                v-model.lazy="form.searchTerm">
          <div class="is-sr-only">
            <button type="submit" class="button secondary" value="Search"></button>
          </div>
        </form>
      </div>
      <div class="navbar-end">
        <a class="navbar-item" href="/about">About</a>
        <a class="navbar-item" href="/collections">Browse by Collection</a>
        <a class="navbar-item is-hidden-desktop" href="/search-help">Search Guide</a>
        <a class="navbar-item" href="/feedback">Feedback</a>
      </div>
    </div>
  </nav>
</template>

<script>
import { SET_QUERY } from '@/store/mutation-types';

export default {
  props: {
    showNavSearch: {
      default: false,
    },
    navSearchPlaceholder: {
      default: 'Search all images',
    },
  },
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

/* header */

.logo > img {
  height: 42px;
  padding-right: 11px;
}


.hero_search-form {
  margin: 0 15px;

  input {
    width: 16rem;
  }
}
</style>
