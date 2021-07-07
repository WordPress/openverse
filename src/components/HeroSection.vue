<template>
  <!-- eslint-disable vuejs-accessibility/no-autofocus -->
  <div class="hero">
    <div class="hero-center has-text-centered">
      <h1 class="title is-2 padding-bottom-normal">
        {{ $t('hero.title') }}
      </h1>
      <h2 class="title is-5 b-header has-text-weight-medium">
        {{ $t('hero.subtitle') }}
      </h2>
      <form
        class="hero-search__form margin-top-larger"
        role="search"
        method="get"
        action="/search"
        @submit.prevent="onSubmit"
      >
        <div class="hero-search__control">
          <input
            id="searchTerm"
            v-model.lazy="form.searchTerm"
            required="required"
            class="hero-search__input input"
            :aria-label="$t('hero.aria.search')"
            autofocus
            type="search"
            name="q"
            :placeholder="$t('hero.search.placeholder')"
            autocapitalize="none"
          />
          <button class="hero-search__button button is-primary" title="Search">
            {{ $t('hero.search.button') }}
          </button>
        </div>
        <div
          class="caption has-text-centered margin-top-big has-text-weight-medium"
        >
          <i18n path="hero.caption.content" tag="p">
            <template #link>
              <a
                href="https://creativecommons.org/share-your-work/licensing-examples/"
                target="_blank"
                :aria-label="$t('hero.aria.caption')"
                rel="noopener"
              >
                {{ $t('hero.caption.link') }}
              </a>
            </template>
          </i18n>
        </div>
        <HomeLicenseFilter />
      </form>
    </div>
    <img
      class="logo-cloud"
      src="~/assets/logo-cloud.png"
      alt="Logos from sources of Openverse licensed images"
    />
  </div>
  <!-- eslint-enable -->
</template>

<script>
import { SET_QUERY } from '~/store-modules/mutation-types'
import { filtersToQueryData } from '~/utils/searchQueryTransform'
import { mapState } from 'vuex'

export default {
  name: 'HeroSection',
  data: () => ({ form: { searchTerm: '' } }),
  computed: {
    ...mapState(['isEmbedded']),
  },
  mounted() {
    if (document.querySelector('#searchTerm')) {
      document.querySelector('#searchTerm').focus()
    }
  },
  methods: {
    onSubmit() {
      this.$store.commit(SET_QUERY, { query: { q: this.form.searchTerm } })
      const newPath = this.localePath({
        path: '/search',
        query: {
          q: this.form.searchTerm,
          ...filtersToQueryData(this.$store.state.filters),
        },
      })
      this.$router.push(newPath)
    },
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
$hero-height-desktop: 85vh;
$hero-height: 55vh;

.hero {
  background: #fff;
  position: relative;
  background-size: cover;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  min-height: $hero-height;
  @include tablet() {
    min-height: $hero-height-desktop;
  }
}
.hero-center {
  margin-top: 4rem;
}
.hero-search {
  &__form {
    position: relative;
    width: 100%;
    padding: 0 0.5em 0 0.5em;
  }
  &__control {
    display: flex;
  }
  &__input {
    margin-right: -1px;
    border-bottom-right-radius: 0;
    border-top-right-radius: 0;
    width: 100%;
    max-width: 100%;
    @include desktop {
      width: 570px;
      font-size: 1.75rem;
      height: 5.063rem;
      padding-left: 1.5rem;
    }
  }
  &__button {
    border-bottom-left-radius: 0;
    border-top-left-radius: 0;
    font-size: 1rem;
    padding: 0.5rem 1.2rem;
    @include desktop {
      font-size: 1.75rem;
      padding: 2.407rem 2.5rem;
    }
  }
}

.help-links {
  z-index: 1;
  position: absolute;
  bottom: 1rem;
  left: 1rem;
}

.help-icon {
  height: 32px;
  vertical-align: middle;
}

.logo-cloud {
  z-index: 0;
  margin-top: auto;
  width: 100%;
  padding-left: 1rem;
  height: 120px;
  object-fit: cover;
  object-position: left center;

  @include desktop {
    object-fit: initial;
    height: auto;
    padding: 0;
    margin-top: 4rem;
    margin-left: auto;
    margin-right: auto;
    width: calc(100% - 1rem);
    max-width: 1400px;
  }
}
</style>
