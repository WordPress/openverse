<template>
<transition name="fade">
<div class="share-bar" v-if="this.images.length>0">
    <div class="grid-x grid-margin-x">
      <div class="share-bar_images cell medium-6 large-6">
        <ul class="share-bar_images-list">
          <li class="share-bar_image-item" v-for="(image, index) in images">
            <transition name="fade">
              <img class="share-bar_image" :src="image.url">
            </transition>
            <span class="share-bar_image-remove-btn"
              @click.prevent="onRemoveImage(image)"></span>
          </li>
        </ul>
      </div>
      <div class="cell medium-6 large-6 grid-x">
        <form v-on:submit.prevent="onCreateList"
              method="post"
              class="cell medium-6 large-8"
              v-if="this.shouldShowList">
          <div class="input-group">
            <div class="input-group-button">
              <input type="submit" class="button" value="Create List" >
            </div>
            <input class="input-group-field"
              type="text"
              placeholder="Name your list"
              required="required"
              v-model="listTitle">
          </div>
        </form>
        <div class="cell medium-6 large-8" v-if="this.shouldShowShare">
          <div class="input-group">
            <div class="input-group-button">
              <span class="input-group-label">List Url</span>
            </div>
            <input class="input-group-field"
              type="text"
              v-model="shareListURL">
          </div>
        </div>
        <div class="share-bar_social-items cell medium-6 large-4"
             v-if="this.shouldShowShare">

          <a class="social-button facebook" href="#"></a>
          <a class="social-button twitter" href="#"></a>
          <a class="social-button instagram" href="#"></a>
        </div>
      </div>
  </div>
</div>
</transition>
</template>

<script>
import { CREATE_LIST } from '@/store/action-types';
import { ADD_IMAGE_TO_LIST, REMOVE_IMAGE_FROM_LIST } from '@/store/mutation-types';

export default {
  name: 'share-bar',
   data:  () => ({
    listTitle: null,
  }),
  computed: {
    images() {
      return this.$store.state.shareListImages;
    },
    shareListURL() {
      return this.$store.state.shareListURL;
    },
    shouldShowList() {
      return this.shareListURL === '';
    },
    shouldShowShare() {
      return this.shareListURL !== '';
    },
  },
  watch: {
    shouldShowList: val => console.log(this)
  },
  methods: {
    getFacebookURL() {

    },
    onCreateList() {
      const imageIDs = this.$store.state.shareListImages.map(image => image.id);

      this.$store.dispatch(CREATE_LIST, {
        listTitle: this.listTitle,
        images: imageIDs
      });
    },
    onRemoveImage(image) {
      this.$store.commit(REMOVE_IMAGE_FROM_LIST, { image });
    },
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss">
  @import '../../node_modules/foundation-sites/scss/foundation';

  .share-bar {
    position: fixed;
    right: 0px;
    bottom: 30px;
    width: 100%;
    overflow-x: scroll;
    background-color: #d6d6d6;
    z-index: 100;
    white-space: nowrap;
    padding: 15px 30px;
  }

  .share-bar_images-list {
    overflow-x: scroll;
    padding: 0;
    margin: 0;
  }

  .share-bar_image-item {
    position: relative;
    padding: 0 5px;
    display: inline-block;
  }

  .share-bar_image-remove-btn {
    cursor: pointer;
    width: 16px;
    height: 16px;
    display: inline-block;
    top: 2px;
    right: 5px;
    position: absolute;
    z-index: 200;

    &:after {
      content: '';
      width: 100%;
      height: 100%;
      display: block;
      background: url('../assets/remove-icon.svg') 16px 16px;
    }
  }

  .share-bar_social-items {
    padding-left: 30px;
  }

  .share-bar_image {
    display: block;
    max-height: 100px;
  }

  $social-button-size: 3.125rem;
  $social-button-border-width: 0.125rem;
  $social-button-font-size: 1.5625rem;
  $social-button-line-height: 2em;
  $social-button-border-radius: 1.6875rem;
  $social-button-transition: all 0.5s ease;
  $social-button-margin: 0.25rem;

  $social-brand-facebook: #3b5998;
  $social-brand-twitter: #55acee;
  $social-brand-instagram: #c32aa3;

  @mixin social-button($brand-color, $brand-icon) {
    background: $brand-color;

    &:before {
      font-family: "FontAwesome";
      content: $brand-icon;
    }
    &:hover,
    &:focus {
      color: $brand-color;
      background: $white;
      border-color: $brand-color;
    }
  }

  .share-bar_social-items {

    .social-button {
      display: inline-block;
      position: relative;
      cursor: pointer;
      width: $social-button-size;
      height: $social-button-size;
      border: $social-button-border-width solid transparent;
      padding: 0;
      text-decoration: none;
      text-align: center;
      color: $white;
      font-size: $social-button-font-size;
      font-weight: normal;
      line-height: $social-button-line-height;
      border-radius: $social-button-border-radius;
      transition: $social-button-transition;
      margin-right: $social-button-margin;
      margin-bottom: $social-button-margin;

      &:hover,
      &:focus {
        transform: rotate(360deg);
      }

      &.facebook {
        @include social-button($social-brand-facebook, "\f09a")
      }

      &.twitter {
        @include social-button($social-brand-twitter, "\f0c4")
      }

      &.instagram {
        @include social-button($social-brand-instagram, "\f16d")
      }
    }
  }

  .fade-enter-active, .fade-leave-active {
    transition: opacity .5s;
  }

  .fade-enter, .fade-leave-to {
    opacity: 0;
  }
</style>
