<template>
  <nav :aria-label="$t('header.aria.primary')" class="navbar">
    <div class="navbar-brand">
      <router-link class="logo" to="/">
        <img alt="Logo" src="/static/logos/products/search.svg" />
      </router-link>
      <a
        role="button"
        :class="{ ['navbar-burger']: true, ['is-active']: isBurgerMenuActive }"
        :aria-label="$t('header.aria.menu')"
        aria-expanded="false"
        @click="toggleBurgerActive"
        v-on:keyup.enter="toggleBurgerActive"
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
            :aria-label="$t('header.aria.search')"
            class="input"
            type="search"
            :placeholder="navSearchPlaceholder"
            v-model.lazy="form.searchTerm"
          />
          <div class="is-sr-only">
            <button
              :aria-label="$t('header.aria.sr-search')"
              tabindex="-1"
              type="submit"
              class="button secondary"
              value="Search"
            ></button>
          </div>
        </form>
      </div>
      <div class="navbar-end">
        <div class="navbar-item has-dropdown is-hoverable">
          <a class="navbar-link is-arrowless">
            {{ $t('header.about-tab') }}
            <i class="icon caret-down" />
          </a>
          <div class="navbar-dropdown">
            <router-link class="navbar-item" to="/about">{{
              $t('header.about')
            }}</router-link>
            <router-link class="navbar-item" to="/sources">{{
              $t('header.source')
            }}</router-link>
            <router-link class="navbar-item" to="/meta-search">{{
              $t('header.meta-search')
            }}</router-link>
            <a
              href="https://creativecommons.org/about/cclicenses/"
              target="_blank"
              rel="noopener"
              class="navbar-item"
              >{{ $t('header.licenses') }}
              <i class="icon external-link" />
            </a>
          </div>
        </div>

        <div class="navbar-item has-dropdown is-hoverable">
          <a class="navbar-link is-arrowless">
            {{ $t('header.resources-tab') }}
            <i class="icon caret-down" />
          </a>
          <div class="navbar-dropdown">
            <router-link class="navbar-item" to="/search-help">{{
              $t('header.search-guide')
            }}</router-link>
            <router-link class="navbar-item" to="/feedback">{{
              $t('header.feedback')
            }}</router-link>
          </div>
        </div>

        <a
          :aria-label="$t('header.aria.extension')"
          class="navbar-item"
          href="https://opensource.creativecommons.org/ccsearch-browser-extension/"
          target="_blank"
        >
          {{ $t('header.extension') }}
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
  },
  name: 'nav-section',
  computed: {
    navSearchPlaceholder() {
      return this.$t('header.placeholder')
    },
  },
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
