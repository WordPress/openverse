<template>
<div class="home-page">
  <header-section showHero="true"></header-section>
  <div class="grid-container">
    <div class="featured-items">
      <div class="row align-middle align-justify featured-items-wrapper">
        <div class="featured-items-brands">
          <h5 class="featured-items-title">Top Categories:</h5>
          <div @click="onCategoryClick('people')" class="featured-item-container">
            <span class="featured-image-banner">People</span>
            <img src="@/assets/people_small.jpg">
          </div>
          <div @click="onCategoryClick('nature')" class="featured-item-container">
            <span class="featured-image-banner">Nature</span>
            <img src="@/assets/nature_small.jpg">
          </div>
          <div @click="onCategoryClick('landscapes')" class="featured-item-container">
            <span class="featured-image-banner">Landscapes</span>
            <img src="@/assets/landscapes_small.jpg">
          </div>
          <div @click="onCategoryClick('animals')" class="featured-item-container">
            <span class="featured-image-banner">Animals</span>
            <img src="@/assets/animals_small.jpg">
          </div>
        </div>
      </div>
    </div>
  <div class="grid">
  <h4 class="grid_header">Top Images</h4>
  <div  class="header-grid">
  <div id="b1" class="block">
    <img src="@/assets/mix-tapes_medum.jpg" />
    <div class="block_overlay">

    </div>
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
  </div>
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


.home-page  .nav {
  position: absolute;
  background: transparent !important;
}

.featured-items {
  border: 1px solid rgba(230, 230, 230, .5);
  margin-top: $vert-seperate;
  margin-bottom: $vert-seperate;
  padding: 1rem 1rem;

  h4 {
    @media screen and (max-width: 39.9375em) {
      font-size: 1.5rem;
    }
  }

  p {
    color: $gray;
  }

  .featured-items-brands {
    flex: 1 0 auto;
    display: flex;
    justify-content: space-around;

    @media screen and (max-width: 39.9375em) {
      flex-wrap: wrap;
      width: 100%;
      }
    }

  .featured-item-container {
    position: relative;
    cursor: pointer;

    a {
      text-decoration: underline;
    }
  }

  .featured-items-title {
    margin-bottom: 0;
  }

  .featured-image-banner {
    background-color: rgba(23, 121, 186, 0.8);
    color: #fefefe;
    font-weight: 600;
    left: 0;
    padding: 0.25rem;
    position: absolute;
    top: 25%;
    width: 75%;
    z-index: 10;
  }

  @media screen and (max-width: 39.9375em) {
    .featured-items-brands img {
      flex-basis: 40%;
      margin-bottom: 1rem;
    }

    .featured-items-title {
      margin-bottom: 1rem;
    }
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
  margin: 30px 0;
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
