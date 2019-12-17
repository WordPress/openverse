<template>
  <div class="hero">
    <h1>Search for free and public domain content</h1>
    <form class="hero_search-form"
          role="search"
          method="get"
          action="/search"
          v-on:submit.prevent="onSubmit">
      <div class="search-form_ctr grid-x">
          <div class="cell large-12">
            <input required="required"
                   autofocus="true"
                   class="hero_search-input"
                   type="search"
                   name="q"
                   placeholder="Search for images..."
                   autocapitalize="none"
                   id="searchTerm"
                   v-model.lazy="form.searchTerm">
          </div>
          <div class="cell large-12">
            <button class="hero_search-btn" title="Search"></button>
          </div>
      </div>
      <div class="description">
        <p>
          All our content is under Creative Commons licenses.
          <a href="https://creativecommons.org/share-your-work/licensing-examples/" target="_blank" rel="noopener">Learn more</a> about CC licenses.
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
}

$hero-height: 71vh;

.hero {
  background: #fff;
  position: relative;
  height: $hero-height;
  background-size: cover;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  min-height: 300px;

  .logo {
    margin-bottom: 4vh;
    height: 7em;

    @media screen and (max-width: 39.9375em), (max-height: 720px) {
      height: 5.5em;
      margin-top: 4vh;
      padding: 0.5em;
    }
  }

  .hero_search-form {
    position: relative;
    margin-top: 0;
    border-radius: 3px;
    max-width: 580px;
    width: 100%;
  }

  .hero_search-input {
    font-size: 24px;
    padding-left: 30px;
    margin-bottom: 0;
    width: 100%;
    height: 60px;
    border-radius: 4px;
    box-shadow: 0 3px 8px 0 rgba(51, 51, 51, 0.13);
    border: solid 1px #d8d8d8;
  }

  .hero_search-input::placeholder {
    color: #333;
    font-size: 25px;
    font-weight: 600;
     font-family: Source Sans Pro;
  }

  .hero_search-btn {
    position: absolute;
    top: 0;
    right: 0;
    height: 60px;
    width: 60px;
    margin: 2px;
    font-size: 24px;
    cursor: pointer;
    transition: all .2s ease-in-out;
    border-radius: 3px;

    &:after {
      content: '';
      background: url('../assets/search-icon_black.svg') center center no-repeat;
      background-size: 20px;
      opacity: 0.7;
      top: 0;
      left: 0;
      bottom: 0;
      right: 0;
      position: absolute;
      z-index: 10;
    }
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
  font-style: italic;
  font-size: 0.8125em;
  margin-top: 1em;
}

.old-search-link {
  position: absolute;
  top: 1rem;
  right: 2rem;

  @media screen and (max-width: 320px) {
    top: 0;
    font-size: 0.9rem;
  }
}

.search-help-link {
  position: absolute;
  bottom: 1rem;
  right: 2rem;

  @media screen and (max-width: 768px) {
    display: none;
  }
}

.help-icon {
  height: 32px;
}

/* Small only */
@media screen and (max-width: 40em) {
  .hero {
    height: 60vh;
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

  .logo {
    height: 5.5em;
  }
}
</style>
