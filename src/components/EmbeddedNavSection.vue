<template>
  <nav :aria-label="$t('header.aria.primary')" class="navbar embedded">
    <div class="navbar-brand has-color-white">
      <a
        role="button"
        :class="{ ['navbar-burger']: true, ['is-active']: isBurgerMenuActive }"
        :aria-label="$t('header.aria.menu')"
        aria-expanded="false"
        @click="toggleBurgerActive"
        @keyup.enter="toggleBurgerActive"
      >
        <span aria-hidden="true" />
        <span aria-hidden="true" />
        <span aria-hidden="true" />
      </a>
    </div>
    <div :class="{ ['navbar-menu']: true, ['is-active']: isBurgerMenuActive }">
      <form
        v-if="showNavSearch"
        class="hero_search-form"
        role="search"
        method="post"
        @submit.prevent="onSubmit"
      >
        <input
          v-model.lazy="form.searchTerm"
          :aria-label="$t('header.aria.search')"
          class="input"
          type="search"
          :placeholder="navSearchPlaceholder"
        />
        <div class="is-sr-only">
          <button
            :aria-label="$t('header.aria.sr-search')"
            tabindex="-1"
            type="submit"
            class="button secondary"
            value="Search"
          />
        </div>
      </form>
      <div class="navbar-end">
        <div class="navbar-item has-dropdown is-hoverable">
          <a class="navbar-link is-arrowless">
            {{ $t('header.about-tab') }}
            <i class="icon caret-down" />
          </a>
          <div class="navbar-dropdown">
            <NuxtLink class="navbar-item" :to="localePath('/about')">
              {{ $t('header.about') }}
            </NuxtLink>
            <NuxtLink class="navbar-item" :to="localePath('/sources')">
              {{ $t('header.source') }}
            </NuxtLink>
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
            <NuxtLink class="navbar-item" :to="localePath('/search-help')">
              {{ $t('header.search-guide') }}
            </NuxtLink>
            <NuxtLink class="navbar-item" :to="localePath('/meta-search')">
              {{ $t('header.meta-search') }}
            </NuxtLink>
            <a
              href="https://api.creativecommons.engineering/"
              target="_blank"
              rel="noopener"
              class="navbar-item"
              >{{ $t('header.api') }}
              <i class="icon external-link" />
            </a>
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
import { SET_QUERY } from '~/store-modules/mutation-types'

export default {
  name: 'EmbeddedNavSection',
  props: {
    showNavSearch: {
      default: false,
    },
  },
  data: () => ({ form: { searchTerm: '' }, isBurgerMenuActive: false }),
  computed: {
    navSearchPlaceholder() {
      return this.$t('header.placeholder')
    },
  },
  methods: {
    onSubmit() {
      this.$store.commit(SET_QUERY, { query: { q: this.form.searchTerm } })
      const newPath = this.localePath({
        path: '/search',
        query: { q: this.form.searchTerm },
      })
      this.$router.push(newPath)
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
.logo {
  color: black;
  font-size: 2rem;
  font-weight: bold;
  &:link,
  &:visited,
  &:hover,
  &:active {
    text-decoration: none;
  }
}

.hero_search-form {
  margin: 0 15px 0 0;
  display: flex;
  align-items: center;

  input {
    width: 16rem;
  }
}
</style>
