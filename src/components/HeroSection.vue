<template>
  <div class="hero">
    <p class="hero_image-attribution">
      <a href="https://www.flickr.com/photos/140462483@N05/36763898452/in/photolist-Y1GAb9-KFbgie-iRNK5P-FwSJtx-r3JwHJ-dmDxZk-2458TsV-sdNGNQ-NiPCqj-HxRj66-21jgWwY-dpcacC-FVoUb7-25LQb3p-DwTY2Q-27khBQQ-HufH3f-229EUc1-HqUu8L-YiecAE-22Xstqx-23q3WXQ-29Zr9UK-23w96zW-27ar4VE-28j1rxF-28GXPmh-25D6ugy-22KJEyo-ihoLz1-22Rg6xT-29FEvvX-EgQ6T1-4xZBHM-CQcEax-9aqoKJ-pfH1iK-qb612F-26zRQdy-218Y6Zo-28PB4Wa-dsYdav-XPFsk9-225xzhN-22eRiqK-XnJxyW-25Gn2yq-27YYYqE-JRw6D2-23rSQWb"
         target="_blank"
         rel="noreferrer">
        Photo by Антон Потемин from flickr
      </a>
      <span class="hero_instagram-icon">&nbsp;</span>
    </p>
    <form class="hero_search-form"
          role="search"
          method="post"
          v-on:submit.prevent="onSubmit">
      <div class="search-form_ctr grid-x">
          <div class="cell large-12">
            <input required="required"
                   autofocus=""
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
  </div>
</template>

<script>
import router from '@/router';

export default {
  name: 'hero',
  data: () => ({ form: { searchTerm: '' } }),
  methods: {
    onSubmit() {
      router.push({ path: 'search', query: { q: this.form.searchTerm } });
    },
  },
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
@import '../../node_modules/foundation-sites/scss/foundation';

$hero-height: 70vh;

.hero {
  position: relative;
  height: $hero-height;
  background: url('../assets/mountain_large.jpg') 50% no-repeat;
  background-size: cover;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  min-height: 300px;

  .hero-text {
    color: $white;
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
    background: rgba(255, 255, 255, 0.4);
    box-shadow: none;
    color: rgba(255, 255, 255, 0.8);
  }

  .hero_search-input::placeholder {
    color: rgba(255, 255, 255, 0.8);
  }

  .hero_search-btn {
    position: absolute;
    top: 0;
    right: 0;
    background: transparent;
    height: calc( 100% - 3px );
    width: 60px;
    margin: 2px;
    font-size: 24px;
    cursor: pointer;
    transition: all .2s ease-in-out;
    border-radius: 3px;

    &:after {
      content: '';
      background: url('../assets/search-icon_white.svg') center center no-repeat;
      background-size: 20px;
      opacity: 0.5;
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

.hero_instagram-icon {
  display: inline-block;
  width: 32px;
  height: 32px;
  background: url('../assets/instagram-icon.png') 50% no-repeat;
}

.hero_image-attribution {
  position: absolute;
  left: 30px;
  bottom: 0;
  z-index: 10;
  font-weight: 500;
  font-size: .8em;

  a {
    color: #fff;

    &:hover {
      text-decoration: underline;
    }
  }
}

/* Small only */
@media screen and (max-width: 39.9375em) {
  .hero {
    height: 60vh;
  }

  .hero_image-attribution {
    left: 15px;
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
