<template class="homepage">
<section>
  <header-section></header-section>
  <div class="grid-container">
    <div class="featured-items">
      <div class="row align-middle align-justify featured-items-wrapper">
        <div class="featured-items-brands">
          <h5 class="featured-items-title">Top Categories:</h5>
          <div @click="onCategoryClick('people')" class="featured-item-container">
            <span class="featured-image-banner">People</span>
            <img src="https://placehold.it/150x70">
          </div>
          <div @click="onCategoryClick('nature')" class="featured-item-container">
            <span class="featured-image-banner">Nature</span>
            <img src="https://placehold.it/150x70">
          </div>
          <div @click="onCategoryClick('landscapes')" class="featured-item-container">
            <span class="featured-image-banner">Landscapes</span>
            <img src="https://placehold.it/150x70">
          </div>
          <div @click="onCategoryClick('animals')" class="featured-item-container">
            <span class="featured-image-banner">Animals</span>
            <img src="https://placehold.it/150x70">
          </div>
        </div>
      </div>
    </div>
    <hr>
    <search-grid></search-grid>
  </div>
  <footer-section></footer-section>
</section>
</template>

<script>
import HeaderSection from '@/components/HeaderSection';
import CardsSection from '@/components/CardsSection';
import SearchGrid from '@/components/SearchGrid';
import FooterSection from '@/components/FooterSection';
import ImageService from '@/api/ImageService';

const Homepage = {
  name: 'Homepage',
  components: {
    HeaderSection,
    CardsSection,
    SearchGrid,
    FooterSection,
  },
  methods: {
    onCategoryClick(category) {
      console.log(category);
    },
  },
  mounted() {
    ImageService.search({ q: 'people, landscapes, nature' })
      .then(results => console.log(results));
  },
};


export default Homepage;


</script>
<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>

$gray: #808080;
$highlight: #4ec6cd;
$nav-text-color: $gray;
$vert-seperate: 4rem;

.featured-items {
  background: lighten($gray, 40%);
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
</style>
