<template>
  <nav :aria-label="$t('header.aria.primary')" class="navbar">
    <div class="navbar-brand text-white">
      <!-- eslint-disable @intlify/vue-i18n/no-raw-text -->
      <NuxtLink class="logo" :to="localePath('/')">
        <img
          alt="Openverse logo mark"
          src="~/assets/logo.svg?data"
          style="padding-right: 24px"
          width="160"
          height="24"
        />
      </NuxtLink>
      <!-- eslint-enable -->
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
      <div v-if="showNavSearch" class="ml-6">
        <form
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
      </div>
      <div class="navbar-end">
        <Dropdown v-slot="{ onFocus }" :text="$t('header.about-tab')">
          <NuxtLink
            class="navbar-item"
            :to="localePath('/about')"
            @focus="onFocus()"
          >
            {{ $t('header.about-nav-item') }}
          </NuxtLink>
          <NuxtLink
            class="navbar-item"
            :to="localePath('/sources')"
            @focus="onFocus()"
          >
            {{ $t('header.source-nav-item') }}
          </NuxtLink>
          <a
            href="https://creativecommons.org/about/cclicenses/"
            target="_blank"
            rel="noopener"
            class="navbar-item"
            @focus="onFocus()"
            >{{ $t('header.licenses-nav-item') }}
            <i class="icon external-link" />
          </a>
        </Dropdown>

        <Dropdown v-slot="{ onFocus }" :text="$t('header.resources-tab')">
          <NuxtLink
            class="navbar-item"
            :to="localePath('/search-help')"
            @focus="onFocus()"
          >
            {{ $t('header.search-guide-nav-item') }}
          </NuxtLink>
          <NuxtLink
            class="navbar-item"
            :to="localePath('/meta-search')"
            @focus="onFocus()"
          >
            {{ $t('header.meta-search-nav-item') }}
          </NuxtLink>
          <NuxtLink
            class="navbar-item"
            :to="localePath('/feedback')"
            @focus="onFocus()"
          >
            {{ $t('header.feedback-nav-item') }}
          </NuxtLink>
          <a
            href="https://api.creativecommons.engineering/v1/"
            target="_blank"
            rel="noopener"
            class="navbar-item"
            @focus="onFocus()"
            >{{ $t('header.api-nav-item') }}
            <i class="icon external-link" />
          </a>
        </Dropdown>

        <a
          class="navbar-item"
          href="https://opensource.creativecommons.org/ccsearch-browser-extension/"
          target="_blank"
        >
          {{ $t('header.extension-nav-item') }}
          <i class="icon external-link" />
        </a>
      </div>
    </div>
  </nav>
</template>

<script>
import { SET_QUERY } from '~/store-modules/mutation-types'
import Dropdown from '~/components/Dropdown'

export default {
  name: 'NavSection',
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
  margin: 0 15px;

  input {
    width: 16rem;
  }
}
</style>
