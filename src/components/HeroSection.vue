<template>
  <div class="hero">
    <img class="logo" src="../assets/cc-logo_large_black.png">
    <form class="hero_search-form"
          role="search"
          method="post"
          v-on:submit.prevent="onSubmit">
      <div class="search-form_ctr grid-x">
          <div class="cell large-12">
            <input required="required"
                   autofocus="true"
                   class="hero_search-input"
                   type="search"
                   placeholder="Search the commons..."
                   autocapitalize="none"
                   id="searchTerm"
                   v-model.lazy="form.searchTerm">
          </div>
          <div class="cell large-12">
            <button class="hero_search-btn" title="Search"></button>
          </div>
      </div>
    </form>
    <div class="description">
        <p>
          Search for free content licensed under the open Creative Commons licenses
          <br />
          You can learn more about Creative Commons licenses <a href="https://creativecommons.org/licenses/">here</a>
        </p>
    </div>
  </div>
</template>

<script>
import { SET_QUERY } from '@/store/mutation-types';

export default {
  name: 'hero',
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

$hero-height: 40vh;

.hero {
  background: #e9ebee;
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

    @media screen and (max-width: 39.9375em) {
      height: 5.5em;
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
    outline: 0;
    border-radius: 3px;
    border-width: 0;
    box-shadow: none;
  }

  .hero_search-input::placeholder {
    color: rgb(130, 130, 130);
  }

  .hero_search-btn {
    position: absolute;
    top: 0;
    right: 0;
    height: calc( 100% - 3px );
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
  margin-top: 2vh;
  font-style: italic;
}

/* Small only */
@media screen and (max-width: 39.9375em) {
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
