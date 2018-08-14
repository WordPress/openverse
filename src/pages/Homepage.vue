<template>
<div class="home-page grid-container full">
  <header-section showHero="true"></header-section>
  <div class="home-page_body">
    <section class="featured-images">
      <header class="featured-images_header">
        <h2 class="featured-items_title">Top Categories:</h2>
      </header>
      <div class="featured-images_inner grid-x grid-margin-x grid-margin-y">
        <div @click="onCategoryClick('people')"
             class="featured-images_item small-6 medium-3 cell">
          <span class="featured-images_banner">People</span>
          <img src="@/assets/people_medium.jpg" alt="">
        </div>
        <div @click="onCategoryClick('nature')"
             class="featured-images_item small-6 medium-3 cell">
          <span class="featured-images_banner">Nature</span>
          <img src="@/assets/nature_medium.jpg" alt="">
        </div>
        <div @click="onCategoryClick('landscapes')"
             class="featured-images_item small-6 medium-3 cell">
          <span class="featured-images_banner">Landscapes</span>
          <img src="@/assets/landscapes_medium.jpg" alt="">
        </div>
        <div @click="onCategoryClick('animals')"
             class="featured-images_item small-6 medium-3 cell">
          <span class="featured-images_banner">Animals</span>
          <img src="@/assets/animals_medium.jpg" alt="">
        </div>
      </div>
    </section>
  <section class="grid">
    <header class="top-images_header">
      <h2 class="featured-items_title">Top Images:</h2>
    </header>
    <div  class="header-grid">
      <div id="b1" class="block">
        <img src="@/assets/mix-tapes_medum.jpg" />
        <div class="block_overlay"></div>
      </div>
      <div id="b2" class="block"></div>
      <div id="b3" class="block"></div>
      <div id="b4" class="block"></div>
      <div class="bottom-block">
        <div id="b5" class="block"></div>
        <div id="b6" class="block"></div>
        <div id="b7" class="block"></div>
      </div>
    </div>
  </section>
  </div>
  <footer-section></footer-section>
</div>
</template>

<script>
import HeaderSection from '@/components/HeaderSection';
import CardsSection from '@/components/CardsSection';
import SearchGrid from '@/components/SearchGrid';
import FooterSection from '@/components/FooterSection';
import router from '@/router';

const HomePage = {
  name: 'home-page',
  components: {
    HeaderSection,
    CardsSection,
    SearchGrid,
    FooterSection,
  },
  methods: {
    onCategoryClick(category) {
      router.push({ path: 'search', query: { q: category } });
    },
  },
};

export default HomePage;
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss">
$gray: #808080;
$highlight: #4ec6cd;
$nav-text-color: $gray;
$vert-seperate: 4rem;

.home-page .nav {
  position: absolute !important;
  background: transparent !important;
}

.home-page_body {
  margin: 60px 30px 0 30px;

  /* Small only */
  @media screen and (max-width: 39.9375em) {
    margin: 60px 15px 0 15px;
  }
}

.featured-images {
  margin: 15px 0 60px 0;
  background: #f7f8f9;
  padding: 30px;
  border: 1px solid #e7e8e9;

  /* Small only */
  @media screen and (max-width: 39.9375em) {
    padding: 30px 15px;
  }
}

.featured-images_item {
  position: relative;
  cursor: pointer;
  max-height: 140px;
  overflow: hidden;

  img {
    border-radius: 2px;
  }
}

.featured-images_banner {
  background-color: rgba(9, 87, 174, .8);
  color: #fefefe;
  font-weight: 600;
  left: 0;
  padding: 0.5rem;
  position: absolute;
  top: 25%;
  width: 75%;
  z-index: 10;
}

.featured-images_header {
  border-top: 1px solid #e7e8e9;

  h2 {
    margin-bottom: 1.07142857em;
    font-size: .875em;
    font-weight: 600;
    letter-spacing: 1px;
    line-height: 1.25;
    text-transform: uppercase;
    display: inline-block;
    padding-top: .28571429em;
    border-top: 5px solid rgba(29, 31, 39, 0.8);
    margin-top: -3px;
  }
}

.top-images_header {
  border-top: 1px solid #e7e8e9;

  h2 {
    margin-bottom: 1.07142857em;
    font-size: .875em;
    font-weight: 600;
    letter-spacing: 1px;
    line-height: 1.25;
    text-transform: uppercase;
    display: inline-block;
    padding-top: .28571429em;
    border-top: 5px solid rgba(29, 31, 39, 0.8);
    margin-top: -3px;
  }
}

.header-grid {
  width: 100%;
  height: 100vh;
  display: grid;
  grid-template-rows: 1fr 1fr 1fr;
  grid-template-columns: repeat(5, 1fr);
  grid-template-areas:
  "big-top big-top big-top small-top small-top"
  "small-middle small-middle big-middle big-middle big-middle"
  "big-bottom big-bottom big-bottom big-bottom big-bottom";
  margin: 15px 0;
}

.block {
  position: relative;
  height: 100%;
  width: 100%;
  max-height: 250px;
  overflow: hidden;
  border: 1px solid white;
  background: black;
  opacity: 0.8;
  transition: opacity 0.2s ease-out;
  cursor: pointer;

  &:hover {
    transition: opacity 0.2s ease-in;
    opacity: 1;

  }
}

.block_overlay {
  position: absolute;
  top: 200px;
}

#b1 {
  grid-area: big-top;

}

#b2 {
  grid-area :small-top;
}

#b3 {
  grid-area: small-middle;
}

#b4 {
  grid-area: big-middle;
}

.bottom-block {
  grid-area: big-bottom;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
}
</style>
