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
      <h2 class="featured-items_title">Top Images</h2>
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
        <figcaption class="grid_item-overlay">
          <a class="grid_overlay-title"
             :href="image.url"
             @click.stop="() => false"
             target="new">
             {{ image.title }}
          </a>
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
          <figcaption class="grid_item-overlay">
            <a class="grid_overlay-title"
               :href="image.url"
               @click.stop="() => false"
               target="new">
               {{ image.title }}
            </a>
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
import router from '@/router';

const HomePage = {
  name: 'home-page',
  components: {
    HeaderSection,
    SearchGrid,
    FooterSection,
  },
  data: () => ({
    images: [
      {
        title: 'Unpublished-Landscapes',
        url: 'https://www.behance.net/gallery/41530879/Unpublished-Landscapes',
        id: 11913497,
        class: 'grid-item block b1',
        src: require('@/assets/record_large.jpg'), // eslint-disable-line global-require
      }, {
        title: 'Exploded Views',
        url: 'https://www.flickr.com/photos/posk/7124858335',
        id: 921892,
        class: 'grid-item block b2',
        src: require('@/assets/lights_large.jpg'), // eslint-disable-line global-require
      }, {
        title: 'Specific_Media_04',
        url: 'https://www.flickr.com/photos/k2space/14051210350',
        id: 7797602,
        class: 'grid-item block b3',
        src: require('@/assets/office_medium.jpg'), // eslint-disable-line global-require
      }, {
        title: 'Glitched Landscapes',
        url: 'https://www.behance.net/gallery/36164749/Glitched-Landscapes',
        id: 11882642,
        class: 'grid-item block b4',
        src: require('@/assets/sky_medium.jpg'), // eslint-disable-line global-require
      },
      {
        title: 'the mountain story',
        url: 'https://www.behance.net/gallery/55404735/the-mountain-story',
        id: 11859713,
        class: 'grid-item block b5',
        src: require('@/assets/mountain_medium.jpg'), // eslint-disable-line global-require
      },
      {
        title: 'Howling Mixed-Breed Brown Dog',
        url: 'https://www.flickr.com/photos/foundanimalsfoundation/8557041595/',
        id: 11723785,
        class: 'grid-item block b6',
        src: require('@/assets/dog_medium.jpg'), // eslint-disable-line global-require
      },
      {
        title: 'Nike FFF Retouching',
        url: 'https://www.behance.net/gallery/51974139/Nike-FFF-Retouching',
        id: 11884100,
        class: 'grid-item block b7',
        src: require('@/assets/soccer_medium.jpg'), // eslint-disable-line global-require
      },
    ],
  }),
  methods: {
    onCategoryClick(category) {
      router.push({ path: 'search', query: { q: category } });
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
  background: transparent !important;
}

.home-page_body {

  /* Small only */
  @media screen and (max-width: 39.9375em) {
    margin: 60px 0 30px;
  }
}

.featured-images {
  margin: 30px 0;
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
  background-color: rgba(38, 45, 29, .8);
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
}

.grid_overlay-title {
  position: absolute;
  display: block;
  bottom: 10px;
  left: 10px;
  z-index: 100;
  color: #fff;

  &:hover {
    text-decoration: underline;
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
}
</style>
