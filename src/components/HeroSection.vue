<template>
  <div class="hero">
    <div class="hero-center">
      <h2 class="has-text-centered">Search for content to reuse</h2>
      <form
        class="hero_search-form margin-top-bigger"
        role="search"
        method="get"
        action="/search"
        v-on:submit.prevent="onSubmit"
      >
        <div class="is-hidden-touch centered-search-box">
          <div class="field has-addons">
            <div class="control">
              <label for="searchTerm" class="is-sr-only">Search</label>
              <input
                required="required"
                autofocus
                class="hero_search-input input is-large"
                type="search"
                name="q"
                placeholder="I would like to see..."
                autocapitalize="none"
                id="searchTerm"
                v-model.lazy="form.searchTerm"
              />
            </div>
            <div class="control">
              <button class="button is-primary big" title="Search">
                Search
              </button>
            </div>
          </div>
        </div>
        <div class="is-hidden-desktop centered-search-box">
          <div class="field has-addons">
            <div class="control mobile-input">
              <label for="searchTerm" class="is-sr-only">Search</label>
              <input
                required="required"
                autofocus
                class="input"
                type="search"
                name="q"
                placeholder="I would like to see..."
                autocapitalize="none"
                id="searchTerm"
                v-model.lazy="form.searchTerm"
              />
            </div>
            <div class="control">
              <button class="button is-primary small" title="Search">
                Search
              </button>
            </div>
          </div>
        </div>
        <div class="caption has-text-centered margin-top-big">
          <p>
            All our content is under Creative Commons licenses.
            <a
              href="https://creativecommons.org/share-your-work/licensing-examples/"
              target="_blank"
              rel="noopener"
              >Learn more</a
            >
            about CC licenses.
          </p>
        </div>
        <home-license-filter />
      </form>
    </div>

    <div class="help-links">
      <span class="margin-right-bigger">
        Go to the
        <a href="https://oldsearch.creativecommons.org/">old CC Search</a>
        portal
      </span>
    </div>

    <img
      class="logo-cloud"
      src="../assets/logo-cloud.png"
      alt="Logos from sources of Creative Commons licensed images"
    />
  </div>
</template>

<script>
import { SET_QUERY } from '@/store/mutation-types'
import HomeLicenseFilter from './HomeLicenseFilter'

export default {
  name: 'hero-section',
  components: {
    HomeLicenseFilter,
  },
  data: () => ({ form: { searchTerm: '' } }),
  mounted() {
    // Autofocus the search input (fallback for browsers without 'autofocus' or other issues)
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

$hero-height: 80vh;

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
    max-width: 750px;
    width: 100%;
    padding: 0 0.5em 0 0.5em;
  }

  .centered-search-box {
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
