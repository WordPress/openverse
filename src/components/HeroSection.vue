<template>
  <div class="hero">
    <h2 class="has-text-centered">Search for content to reuse</h2>
    <form class="hero_search-form margin-top-bigger"
          role="search"
          method="get"
          action="/search"
          v-on:submit.prevent="onSubmit">
      <div class="is-hidden-touch centered-search-box">
        <div class="field has-addons">
          <div class="control">
            <input required="required"
                class="hero_search-input input is-large"
                type="search"
                name="q"
                placeholder="I would like to see..."
                autocapitalize="none"
                id="searchTerm"
                v-model.lazy="form.searchTerm" />
          </div>
          <div class="control">
            <button class="button is-primary big" title="Search">Search</button>
          </div>
        </div>
      </div>
      <div class="is-hidden-desktop centered-search-box">
        <div class="field has-addons">
          <div class="control mobile-input">
            <input required="required"
                class="input"
                type="search"
                name="q"
                placeholder="I would like to see..."
                autocapitalize="none"
                id="searchTerm"
                v-model.lazy="form.searchTerm" />
          </div>
          <div class="control">
            <button class="button is-primary small" title="Search">Search</button>
          </div>
        </div>
      </div>
      <div class="caption has-text-centered margin-top-big">
        <p>
          All our content is under Creative Commons licenses.
          <a href="https://creativecommons.org/share-your-work/licensing-examples/" target="_blank" rel="noopener">Learn more</a>
          about CC licenses.
        </p>
      </div>
      <home-license-filter />
    </form>
    <div class="help-links is-hidden-mobile">
      <span class="margin-right-bigger">
        Go to the
        <a href="https://oldsearch.creativecommons.org/">old CC Search</a> portal
      </span>

      <span>
        See our
        <a href="/search-help">
          Search Syntax Guide
        </a>
      </span>
    </div>
  </div>
</template>

<script>
import { SET_QUERY } from '@/store/mutation-types';
import HomeLicenseFilter from './HomeLicenseFilter';


export default {
  name: 'hero-section',
  components: {
    HomeLicenseFilter,
  },
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
@import "node_modules/bulma/sass/utilities/initial-variables";
@import "node_modules/bulma/sass/utilities/derived-variables";
@import "node_modules/bulma/sass/utilities/mixins";

$hero-height: 74vh;

.hero {
  background: #fff;
  position: relative;
  height: $hero-height;
  background-size: cover;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  min-height: 300px;

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

  /* Small only */
  @include mobile {
    height: 80vh;
  }
}

.help-links {
  position: absolute;
  bottom: 5rem;
  left: 2rem;
}

.help-icon {
  height: 32px;
  vertical-align: middle;
}
</style>
