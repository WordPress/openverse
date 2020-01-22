<template>
  <div class="hero">
    <h1>Search for content to reuse</h1>
    <form class="hero_search-form"
          role="search"
          method="get"
          action="/search"
          v-on:submit.prevent="onSubmit">
      <div>
        <input required="required"
                autofocus="true"
                class="hero_search-input"
                type="search"
                name="q"
                placeholder="Search for images..."
                autocapitalize="none"
                id="searchTerm"
                v-model.lazy="form.searchTerm" />
        <button class="hero_search-btn" title="Search">Search</button>
      </div>
      <div class="description">
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
@import '../../node_modules/foundation-sites/scss/foundation';

h1 {
  font-family: Roboto;
  font-size: 2.375em;
  color: #333333;
  text-align: center;

  @media screen and (max-width: 40em) {
    font-size: 1.8em;
  }
}

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
    margin-top: 0;
    border-radius: 3px;
    max-width: 750px;
    width: 100%;
    padding: 0 0.5em 0 0.5em;
  }

  .hero_search-input {
    font-size: 24px;
    padding-left: 30px;
    margin-bottom: 0;
    width: 75%;
    height: 70px;
    border-radius: 4px;
    box-shadow: 0 3px 8px 0 rgba(51, 51, 51, 0.13);
    border: solid 1px #d8d8d8;
    float: left;
  }

  .hero_search-input::placeholder {
    color: rgb(192, 192, 192);
    font-size: 25px;
    font-weight: 600;
     font-family: Source Sans Pro;
  }

  .hero_search-btn {
    width: 25%;
    height: 70px;
    border-radius: 4px;
    background-color: #fb7729;
    font-size: 24px;
    cursor: pointer;
    font-family: Roboto;
    font-size: 1.5625em;
    color: #fff;
    text-transform: capitalize;
  }

  &:before {
    content: '';
    position: absolute;
    background: linear-gradient(to top,
                rgba(0, 0, 0, 0.1) 0%,
                rgba(17, 17, 17, 0.7) 100%);
  }
}

.description {
  font-size: 0.8125em;
  margin-top: 1em;
  text-align: center;
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

  .hero .hero_search-input {
    font-size: 20px;
    padding-left: 15px;
  }

  .hero .hero_search-btn {
    right: 10px;
  }
}
</style>
