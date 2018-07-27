<template>
  <header class="header">
    <nav-section></nav-section>
    <div class="hero-section">
      <p class="hero-section_image-attribution">
        <a href="https://www.pexels.com/photo/group-of-people-on-road-with-assorted-color-smokes-889545/"
           target="_blank"
           rel="noreferrer">
          Photo by GEORGE DESIPRIS from Pexels
        </a>
      </p>
      <search-form></search-form>
    </div>
  </header>
</template>

<script>
import NavSection from '@/components/NavSection';
import SearchForm from '@/components/SearchForm';

export default {
  name: 'header-section',
  components: {
    NavSection,
    SearchForm,
  },
  data() {
    return {
      msg: 'Share, Collaborate, Remix, Reuse',
    };
  },
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss">
@import '../../node_modules/foundation-sites/scss/foundation';

$hero-height: 60vh;

.hero-section {
  position: relative;
  background: url('../assets/street_large.jpg') 50% no-repeat;
  background-size: cover;
  height: $hero-height;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;

  .hero-section-text {
    color: $white;
  }

  .search-form {
    margin-top: 0;
    border-radius: 3px;
  }

  &:before {
    content: '';
    position: absolute;
    background: linear-gradient(to top,
                rgba(0, 0, 0, 0.1) 0%,
                rgba(17, 17, 17, 0.7) 100%);
  }
}

.hero-section_image-attribution {
  position: absolute;
  left: 30px;
  bottom: 0;
  z-index: 10;
  font-weight: 700;
  font-size: .8em;

  a {
    color: #fff;

    &:hover {
      text-decoration: underline;
    }
  }
}

.header nav {
  z-index: 10;
}


</style>
