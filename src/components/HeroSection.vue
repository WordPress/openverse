<template>
  <div class="hero">
    <h2 class="has-text-centered">Search for content to reuse</h2>
    <form class="hero_search-form margin-top-normal"
          role="search"
          method="get"
          action="/search"
          v-on:submit.prevent="onSubmit">
      <div class="is-hidden-touch is-flex centered-search-box">
        <input required="required"
                autofocus="true"
                class="hero_search-input input is-large"
                type="search"
                name="q"
                placeholder="Search for images..."
                autocapitalize="none"
                id="searchTerm"
                v-model.lazy="form.searchTerm" />
        <button class="button is-primary big" title="Search">Search</button>
      </div>
      <div class="is-hidden-desktop is-flex centered-search-box">
        <input required="required"
                autofocus="true"
                class="hero_search-input input"
                type="search"
                name="q"
                placeholder="Search for images..."
                autocapitalize="none"
                id="searchTerm"
                v-model.lazy="form.searchTerm" />
        <button class="button is-primary" title="Search">Search</button>
      </div>
      <div class="caption has-text-centered">
        <p>
          All content here is marked as being available for reuse
          under a Creative Commons legal tool. Learn more
          <a href="https://creativecommons.org/share-your-work/licensing-examples/" target="_blank" rel="noopener">here</a>.
        </p>
      </div>
      <home-license-filter />
    </form>
    <div class="old-search-link">
      <span>
        Looking for the old CC Search portal? Go
        <a href="https://oldsearch.creativecommons.org/">here</a>
      </span>
    </div>

    <div class="search-help-link">
      <span>
        See our Search Syntax Guide
        <a href="/search-help">
          here
          <img class='help-icon'
              src='../assets/help_icon.svg'
              alt='Help' />
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


$hero-height: 71vh;

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
    width: 70%;
  }
}

.old-search-link {
  position: absolute;
  top: 1rem;
  right: 2rem;

  @media screen and (max-width: 40em) {
    display: none;
  }
}

.search-help-link {
  position: absolute;
  bottom: 2rem;
  right: 2rem;

  @media screen and (max-width: 40em) {
    display: none;
  }
}

.help-icon {
  height: 32px;
}

/* Small only */
@media screen and (max-width: 40em) {
  .hero {
    height: 80vh;
  }
  .search-form_ctr {
    padding: 0 .9375rem;
  }
}

.is-large {
  height: 70px;
}
</style>
