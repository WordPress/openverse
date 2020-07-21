<template>
  <nav aria-label="primary" class="navbar small">
    <div class="navbar-brand">
      <a class="logo" href="/">
        <img alt="Logo" src="/static/logos/products/search.svg" />
      </a>
      <a
        role="button"
        :class="{ ['navbar-burger']: true, ['is-active']: isBurgerMenuActive }"
        aria-label="menu"
        aria-expanded="false"
        @click="toggleBurgerActive"
      >
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
        <span aria-hidden="true"></span>
      </a>
    </div>
    <div :class="{ ['navbar-menu']: true, ['is-active']: isBurgerMenuActive }">
      <div class="margin-left-big" v-if="showNavSearch === 'true'">
        <form
          class="hero_search-form"
          role="search"
          method="post"
          v-on:submit.prevent="onSubmit"
        >
          <input
            aria-label="search"
            class="input"
            type="search"
            :placeholder="navSearchPlaceholder"
            v-model.lazy="form.searchTerm"
          />
          <div class="is-sr-only">
            <button
              aria-label="sr search button"
              tabindex="-1"
              type="submit"
              class="button secondary"
              value="Search"
            ></button>
          </div>
        </form>
      </div>
      <div class="navbar-end">
        <a class="navbar-item" href="/about">About</a>
        <a class="navbar-item" href="/collections">Collections</a>
        <a class="navbar-item" href="/search-help">Search Guide</a>
        <a class="navbar-item" href="/feedback">Feedback</a>
        <a
          class="navbar-item"
          href="https://opensource.creativecommons.org/ccsearch-browser-extension/"
          target="_blank"
        >
          Extension
          <i class="icon external-link" />
        </a>
      </div>
    </div>
  </nav>
</template>

<script>
import { SET_QUERY } from '@/store/mutation-types'

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
  data: () => ({ form: { searchTerm: '' }, isBurgerMenuActive: false }),
  methods: {
    onSubmit() {
      this.$store.commit(SET_QUERY, {
        query: { q: this.form.searchTerm },
        shouldNavigate: true,
      })
    },
    toggleBurgerActive() {
      this.isBurgerMenuActive = !this.isBurgerMenuActive
    },
  },
}
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
