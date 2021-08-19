<template>
  <nav :aria-label="$t('header.aria.primary')" class="navbar embedded">
    <NuxtLink to="/" style="align-self: center; line-height: 0">
      <img
        alt="Openverse logo mark"
        src="~/assets/logo.svg?data"
        style="padding-right: 24px"
        width="160"
        height="24"
      />
    </NuxtLink>
    <div class="navbar-brand text-white">
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
        <div class="sr-only">
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
        <Dropdown v-slot="{ onFocus }" :text="$t('header.about-tab')">
          <NuxtLink
            class="navbar-item"
            :to="localePath('/about')"
            role="menuitem"
            @focus="onFocus()"
          >
            {{ $t('header.about') }}
          </NuxtLink>
          <NuxtLink
            class="navbar-item"
            :to="localePath('/sources')"
            role="menuitem"
            @focus="onFocus()"
          >
            {{ $t('header.source') }}
          </NuxtLink>
          <a
            href="https://creativecommons.org/about/cclicenses/"
            target="_blank"
            rel="noopener"
            class="navbar-item"
            role="menuitem"
            @focus="onFocus()"
            >{{ $t('header.licenses') }}
            <i class="icon external-link" />
          </a>
        </Dropdown>

        <Dropdown v-slot="{ onFocus }" :text="$t('header.resources-tab')">
          <NuxtLink
            class="navbar-item"
            :to="localePath('/search-help')"
            role="menuitem"
            @focus="onFocus()"
          >
            {{ $t('header.search-guide') }}
          </NuxtLink>
          <NuxtLink
            class="navbar-item"
            :to="localePath('/meta-search')"
            role="menuitem"
            @focus="onFocus()"
          >
            {{ $t('header.meta-search') }}
          </NuxtLink>
          <NuxtLink
            class="navbar-item"
            :to="localePath('/feedback')"
            role="menuitem"
            @focus="onFocus()"
          >
            {{ $t('header.feedback') }}
          </NuxtLink>
          <a
            href="https://api.creativecommons.engineering/"
            target="_blank"
            rel="noopener"
            role="menuitem"
            class="navbar-item"
            @focus="onFocus()"
            >{{ $t('header.api') }}
            <i class="icon external-link" />
          </a>
        </Dropdown>

        <NuxtLink class="navbar-item" :to="localePath('/extension')">
          {{ $t('header.extension') }}
        </NuxtLink>
      </div>
    </div>
  </nav>
</template>

<script>
import { SET_QUERY } from '~/store-modules/mutation-types'
import Dropdown from '~/components/Dropdown'

export default {
  name: 'EmbeddedNavSection',
  components: { Dropdown },
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
