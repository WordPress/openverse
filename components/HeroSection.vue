<template>
  <main class="hero" role="main">
    <div class="hero-center has-text-centered">
      <!-- <div class="locale-block"><locale-selector /></div> -->
      <h1 class="title is-2 padding-bottom-normal">{{ $t('hero.title') }}</h1>
      <h5 class="b-header">{{ $t('hero.subtitle') }}</h5>
      <form
        class="hero_search-form margin-top-bigger"
        role="search"
        method="get"
        action="/search"
        v-on:submit.prevent="onSubmit"
      >
        <div class="is-hidden-touch centered-search-box">
          <div class="field has-addons">
            <div class="control mobile-input">
              <input
                required="required"
                class="hero_search-input input is-large"
                :aria-label="$t('hero.aria.search')"
                autofocus
                type="search"
                name="q"
                :placeholder="$t('hero.search.placeholder')"
                autocapitalize="none"
                id="searchTerm"
                v-model.lazy="form.searchTerm"
              />
            </div>
            <div class="control">
              <button class="button is-primary big" title="Search">
                {{ $t('hero.search.button') }}
              </button>
            </div>
          </div>
        </div>
        <div class="is-hidden-desktop centered-search-box">
          <div class="field has-addons">
            <div class="control mobile-input">
              <input
                required="required"
                class="input"
                :aria-label="$t('hero.aria.search')"
                type="search"
                name="q"
                :placeholder="$t('hero.search.placeholder')"
                autocapitalize="none"
                id="searchTerm"
                v-model.lazy="form.searchTerm"
              />
            </div>
            <div class="control">
              <button class="button is-primary small" title="Search">
                {{ $t('hero.search.button') }}
              </button>
            </div>
          </div>
        </div>
        <div class="caption has-text-centered margin-top-big">
          <i18n path="hero.caption.content" tag="p">
            <template v-slot:link>
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
        <home-license-filter />
      </form>
      <div class="help-links is-hidden-mobile">
        <i18n
          path="hero.old-cc-search.label"
          tag="span"
          class="margin-right-bigger"
        >
          <template v-slot:link>
            <a
              href="https://oldsearch.creativecommons.org/"
              :aria-label="$t('hero.aria.old-cc-search')"
              >{{ $t('hero.old-cc-search.link') }}</a
            >
          </template>
        </i18n>
      </div>
    </div>
    <img
      class="logo-cloud"
      src="../assets/logo-cloud.png"
      alt="Logos from sources of Creative Commons licensed images"
    />
  </main>
</template>

<script>
import { SET_QUERY } from '../store/mutation-types'
import HomeLicenseFilter from './HomeLicenseFilter'
export default {
  name: 'hero-section',
  components: {
    HomeLicenseFilter,
  },
  data: () => ({ form: { searchTerm: '' } }),
  mounted() {
    if (document.querySelector('#searchTerm')) {
      document.querySelector('#searchTerm').focus()
    }
  },
  methods: {
    onSubmit() {
      this.$store.commit(SET_QUERY, {
        query: { q: this.form.searchTerm },
        shouldNavigate: true,
      })
    },
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
@import 'node_modules/bulma/sass/utilities/initial-variables';
@import 'node_modules/bulma/sass/utilities/derived-variables';
@import 'node_modules/bulma/sass/utilities/mixins';

$hero-height: 85vh;

.hero {
  background: #fff;
  position: relative;
  background-size: cover;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  min-height: $hero-height;

  .hero_search-form {
    position: relative;
    width: 100%;
    padding: 0 0.5em 0 0.5em;
  }

  .centered-search-box {
    justify-content: center;
  }

  .field {
    justify-content: center;
  }

  .hero_search-input {
    width: 570px;
  }

  .mobile-input {
    width: 100%;
  }
}

.hero-center {
  margin-top: auto;
  .locale-block {
    position: absolute;
    top: 2.5rem;
    right: 4rem;
  }

  @include tablet {
    .locale-block {
      top: 0rem;
      left: auto;
      right: 4rem;
    }
  }

  /* Small only */
  @include mobile {
    height: auto;
    .locale-block {
      position: relative;
      top: 0rem;
      right: 0rem;
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

  @include tablet {
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
