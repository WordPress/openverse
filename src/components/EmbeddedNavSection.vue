<template>
  <!-- Refer to the Bulma docs for markup: https://bulma.io/documentation/components/navbar/ -->
  <nav
    role="navigation"
    class="navbar embedded"
    :aria-label="$t('header.aria.primary')"
  >
    <div class="navbar-brand flex-grow md:flex-grow-0">
      <NuxtLink
        to="/"
        class="navbar-item"
        style="align-self: center; line-height: 0"
      >
        <!-- width and height chosen w.r.t. viewBox "0 0 280 42" -->
        <OpenverseLogo
          :style="{ width: '160px', height: '24px' }"
          alt="Openverse logo mark"
        />
      </NuxtLink>

      <!-- Hamburger menu -->
      <a
        role="button"
        class="navbar-burger"
        :class="{ 'is-active': isBurgerMenuActive }"
        :aria-label="$t('header.aria.menu')"
        aria-expanded="false"
        @click="toggleBurgerActive"
        @keyup.enter="toggleBurgerActive"
      >
        <span v-for="i in 3" :key="i" aria-hidden="true" />
      </a>
    </div>

    <div class="navbar-menu" :class="{ 'is-active': isBurgerMenuActive }">
      <div class="navbar-start">
        <form
          v-if="showNavSearch"
          class="navbar-item flex items-center"
          role="search"
          method="post"
          @submit.prevent="onSubmit"
        >
          <input
            v-model.lazy="form.searchTerm"
            :aria-label="$t('header.aria.search')"
            class="input w-64"
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
            role="menuitem"
            @focus="onFocus()"
          >
            {{ $t('header.about-nav-item') }}
          </NuxtLink>
          <NuxtLink
            class="navbar-item"
            :to="localePath('/sources')"
            role="menuitem"
            @focus="onFocus()"
          >
            {{ $t('header.source-nav-item') }}
          </NuxtLink>
          <a
            href="https://creativecommons.org/about/cclicenses/"
            target="_blank"
            rel="noopener"
            class="navbar-item"
            role="menuitem"
            @focus="onFocus()"
            >{{ $t('header.licenses-nav-item') }}
            <VIcon class="inline ms-2" :icon-path="externalLinkIcon" rtl-flip />
          </a>
        </Dropdown>

        <Dropdown v-slot="{ onFocus }" :text="$t('header.resources-tab')">
          <NuxtLink
            class="navbar-item"
            :to="localePath('/search-help')"
            role="menuitem"
            @focus="onFocus()"
          >
            {{ $t('header.search-guide-nav-item') }}
          </NuxtLink>
          <NuxtLink
            class="navbar-item"
            :to="localePath('/meta-search')"
            role="menuitem"
            @focus="onFocus()"
          >
            {{ $t('header.meta-search-nav-item') }}
          </NuxtLink>
          <NuxtLink
            class="navbar-item"
            :to="localePath('/feedback')"
            role="menuitem"
            @focus="onFocus()"
          >
            {{ $t('header.feedback-nav-item') }}
          </NuxtLink>
          <a
            href="https://api.openverse.engineering/v1/"
            target="_blank"
            rel="noopener"
            role="menuitem"
            class="navbar-item"
            @focus="onFocus()"
            >{{ $t('header.api-nav-item') }}
            <VIcon class="inline ms-2" :icon-path="externalLinkIcon" rtl-flip />
          </a>
        </Dropdown>

        <NuxtLink class="navbar-item" :to="localePath('/extension')">
          {{ $t('header.extension-nav-item') }}
        </NuxtLink>
      </div>
    </div>
  </nav>
</template>

<script>
import { mapActions } from 'vuex'

import Dropdown from '~/components/Dropdown'
import VIcon from '~/components/VIcon/VIcon.vue'

import { UPDATE_QUERY } from '~/constants/action-types'
import { SEARCH } from '~/constants/store-modules'

import OpenverseLogo from '~/assets/logo.svg?inline'
import externalLinkIcon from '~/assets/icons/external-link.svg'

export default {
  name: 'EmbeddedNavSection',
  components: {
    VIcon,
    Dropdown,
    OpenverseLogo,
  },
  props: {
    showNavSearch: {
      default: false,
    },
  },
  data: () => ({
    form: { searchTerm: '' },
    isBurgerMenuActive: false,
    externalLinkIcon,
  }),
  computed: {
    navSearchPlaceholder() {
      return this.$t('header.placeholder')
    },
  },
  methods: {
    ...mapActions(SEARCH, { setSearchTerm: UPDATE_QUERY }),
    onSubmit() {
      const q = this.form.searchTerm
      this.setSearchTerm({ q })
      const newPath = this.localePath({
        path: '/search',
        query: { q },
      })
      this.$router.push(newPath)
    },
    toggleBurgerActive() {
      this.isBurgerMenuActive = !this.isBurgerMenuActive
    },
  },
}
</script>
