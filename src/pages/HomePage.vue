<template>
<div class="home-page grid-container full">
  <header-section showHero="true"></header-section>
  <div class="home-page_body">
    <section class="featured-images">
      <header class="featured-images_header">
        <h2 class="featured-items_title">Top Categories</h2>
      </header>
      <div class="featured-images_inner
                  grid-x
                  grid-margin-x
                  grid-margin-y">
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
  <section class="grid top-images">
    <header class="top-images_header">
      <h2 class="featured-items_title">Top Picks</h2>
    </header>
    <div  class="header-grid">
      <figure v-for="(image, index) in images" v-if="index < 4"
           :class="image.class" :key="index"
           @click="onGotoDetailPage(image)">
         <a :href="image.url"
             @click.prevent="() => false"
             target="new">
          <img :src="image.src" />
        </a>
        <figcaption class="grid_item-overlay grid_item-overlay__top">
          <license-icons :image="image"></license-icons>
        </figcaption>
        <figcaption class="grid_item-overlay
                           grid_item-overlay__bottom">
          <div @click.stop="() => false"
               class="grid_overlay-title"
               v-html="image.title"
               target="new"></div>
        </figcaption>
      </figure>
      <div class="bottom-block">
        <figure v-for="(image, index) in images" v-if="index > 3"
             :class="image.class" :key="index"
             @click="onGotoDetailPage(image)">
           <a :href="image.url"
              @click.prevent="() => false"
              target="new">
            <img :src="image.src" />
          </a>
          <figcaption class="grid_item-overlay
                             grid_item-overlay__top">
            <license-icons :image="image"></license-icons>
          </figcaption>
          <figcaption class="grid_item-overlay grid_item-overlay__bottom">
            <div class="grid_overlay-title"
                 target="new"
                 @click.stop="() => false"
                 v-html="image.title"></div>
          </figcaption>
        </figure>
      </div>
    </div>
  </section>
  </div>
  <footer-section></footer-section>
</div>
</template>

<script>
import HeaderSection from '@/components/HeaderSection';
import SearchGrid from '@/components/SearchGrid';
import FooterSection from '@/components/FooterSection';
import LicenseIcons from '@/components/LicenseIcons';
import { SET_QUERY } from '@/store/mutation-types';

const HomePage = {
  name: 'home-page',
  components: {
    HeaderSection,
    SearchGrid,
    LicenseIcons,
    FooterSection,
  },
  data: () => ({
    images: [
      {
        class: 'grid-item block b1',
        id: '2b091d94-e72f-46a8-a1b2-ab23ab9ceedf',
        license: 'pdm',
        license_version: '1.0',
        src: 'https://c1.staticflickr.com/1/153/433793895_116a0d7739_b.jpg',
        title: '<a href="https://www.flickr.com/photos/pingnews/433793895/">"Released to Public: Hubble Looks at Monocerotis by NASA, ESA, and Hubble Heritage Team  (NASA)"</a>',
        url: 'https://www.flickr.com/photos/pingnews/433793895/',
      },
      {
        class: 'grid-item block b2',
        id: '740aec57-acaa-4734-92b4-61bc967fecb9',
        license: 'pdm',
        license_version: '1.0',
        src: 'https://c1.staticflickr.com/1/83/263570357_e1b9792c7a_b.jpg',
        title: '<a href="https://www.flickr.com/photos/pingnews/263570357/">"Released to Public: Earth, Image by Reto St\xf6ckli  (NASA)"</a>',
        url: 'https://www.flickr.com/photos/pingnews/263570357/',
      },
      {
        class: 'grid-item block b3',
        id: 'fb1b5814-e0b4-4fe4-9f57-7cd3b5096404',
        license: 'pdm',
        license_version: '1.0',
        src: 'https://c1.staticflickr.com/1/118/288983182_2d827a5c12_b.jpg',
        title: '<a href="https://www.flickr.com/photos/pingnews/288983182/">"Released to Public: Wilber and Orville Wright with Flyer II at Huffman Prairie, 1904 (NASA GPN-2002-000126)"</a>',
        url: 'https://www.flickr.com/photos/pingnews/288983182/',
      },
      {
        class: 'grid-item block b4',
        id: '2cbf4a64-28ea-454a-86e2-ae52c1b93a8a',
        license: 'pdm',
        license_version: '1.0',
        src: 'https://c1.staticflickr.com/1/101/288969363_86b1d5272b_b.jpg',
        title: '<a href="https://www.flickr.com/photos/pingnews/288969363/">"Released to Public: Bald Eagle by Gary Rothstein (NASA KSC-06PD-2063)"</a>',
        url: 'https://www.flickr.com/photos/pingnews/288969363/',
      },
      {
        class: 'grid-item block b5',
        id: 'be846374-26f0-4d2e-9909-f87be38f4143',
        license: 'pdm',
        license_version: '1.0',
        src: 'https://c1.staticflickr.com/1/113/272548043_9c54afe218_b.jpg',
        title: '<a href="https://www.flickr.com/photos/pingnews/272548043/">"Public Domain: World Trade Center Memorial by Denise Gould (DOD Photo 060911-F-9471G-006)"</a>',
        url: 'https://www.flickr.com/photos/pingnews/272548043/',
      },
      {
        class: 'grid-item block b6',
        id: 'ea89aea5-c51d-4642-825e-081ace7f6cb7',
        license: 'pdm',
        license_version: '1.0',
        src: 'https://c2.staticflickr.com/2/1319/1441114164_7704547ff8.jpg',
        title: '<a href="https://www.flickr.com/photos/pingnews/1441114164/">"Public Domain: Franklin D. Roosevelt on the U.S.S. Houston in Charleston, South Carolina, 03/03/1939 (NARA)"</a>',
        url: 'https://www.flickr.com/photos/pingnews/1441114164/',
      },
      {
        class: 'grid-item block b7',
        id: 'b80df152-fe77-4f49-a048-f0891184a1c0',
        license: 'pdm',
        license_version: '1.0',
        src: 'https://c1.staticflickr.com/1/183/436664034_9a6e990ca0_b.jpg',
        title: '<a href="https://www.flickr.com/photos/pingnews/436664034/">"Released to Public: Space Shuttle Discovery Catches a Ride by Lori Losey/NASA, August 19, 2005 (NASA)"</a>',
        url: 'https://www.flickr.com/photos/pingnews/436664034/',
      },
    ],
  }),
  methods: {
    onCategoryClick(category) {
      this.$store.commit(SET_QUERY, { query: { q: category }, shouldNavigate: true });
    },
    onGotoDetailPage(image) {
      this.$router.push(`/photos/${image.id}`);
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

  .badge {
   display: none;
  }
}

.home-page_body {

  /* Small only */
  @media screen and (max-width: 39.9375em) {
    margin: 60px 0 30px;
  }
}

.featured-images {
  margin: 30px 0;
  padding: 30px;

  &_header {
    padding-bottom: 10px;
  }

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
  background-color: rgba(12, 10, 14, .7);
  color: #fefefe;
  font-weight: 600;
  left: 0;
  padding: 0.5rem;
  position: absolute;
  top: 25%;
  width: 16.85em;
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

.top-images {
  padding: 30px;

  /* Small only */
  @media screen and (max-width: 39.9375em) {
    padding: 15px;
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

  /* Small only */
  @media screen and (max-width: 39.9375em) {
    display: block;
    height: auto;
  }
}

.grid-item {
  overflow: hidden;

  &:hover .grid_item-overlay {
    opacity: 1;
    bottom: 0;
  }
}

.grid_item-overlay {
  opacity: 0;
  transition: all .4s ease;
  position: absolute;
  width: 100%;
  height: 20%;
  bottom: -100%;
  color: #fff;
  background: linear-gradient(to top, rgba(0,0,0,.5) 0, rgba(0,0,0,0) 100%);
  padding: 10px;

  &__top {
    height: 20px;
    transition: all .5s ease;
    background: linear-gradient(to bottom,
                rgba(0,0,0,.5)
                0,
                rgba(0,0,0,0) 100%);
    top: 0;

    .photo-license-icons {
      height: 20px !important;
    }
  }

  &__bottom {
    height: 30px;
    background: linear-gradient(to top,
                rgba(0,0,0,.5)
                0,
                rgba(0,0,0,0) 100%);
    bottom: -100%;
    top: auto;
  }

  /* Small only */
  @media screen and (max-width: 39.9375em) {
    bottom: 0;
    opacity: 1;
  }
}

.grid_overlay-title {
  position: absolute;
  display: block;
  bottom: 10px;
  left: 10px;
  z-index: 100;
  color: #fff;

  a {
    color: #fff !important;

    &:hover {
      text-decoration: underline;
    }
  }

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

.b1 {
  grid-area: big-top;

}

.b2 {
  grid-area :small-top;
}

.b3 {
  grid-area: small-middle;
}

.b4 {
  grid-area: big-middle;
}

.bottom-block {
  grid-area: big-bottom;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;

  /* Small only */
  @media screen and (max-width: 39.9375em) {
    display: block;
    height: auto;
  }
}
</style>
