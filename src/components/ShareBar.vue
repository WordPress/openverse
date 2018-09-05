<template>
<transition name="fade">
<div class="share-bar" v-if="this.isVisible">
    <div class="grid-x grid-margin-x">
      <a href="#" @click.prevent="onCloseBar" class="share-bar_close-btn">close</a>
      <div class="share-bar_images cell medium-6 large-6">
        <ul class="share-bar_images-list">
          <li class="share-bar_image-item"
              v-for="(image, index) in images"
              :key="index">
            <transition name="fade">
              <img class="share-bar_image" :src="image.thumbnail || image.url">
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
          <a class="social-button facebook"
             target="_blank"
             :href="`https://www.facebook.com/sharer/sharer.php?u=${this.shareListURL}
              &t==${shareText}&href=${this.shareListURL}`"></a>
          <a class="social-button twitter"
             target="_blank"
             :href="`https://twitter.com/intent/tweet?text=${shareText}`"
          ></a>
          <a class="social-button pinterest"
             target="_blank"
             :href="`https://www.pinterest.com/pin/create/bookmarklet/?media=${images[0].url}&description=${shareText}`"></a>
        </div>
      </div>
  </div>
</div>
</transition>
</template>

<script>
import { CREATE_LIST } from '@/store/action-types';
import { REMOVE_IMAGE_FROM_LIST } from '@/store/mutation-types';

export default {
  name: 'share-bar',
  data: () => ({
    listTitle: null,
    _isVisible: false,
  }),
  computed: {
    shareText() {
      return encodeURI(`I created an image list @creativecommons: ${this.shareListURL}`);
    },
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
    isVisible: {
      get() {
        return this.$data._isVisible;
      },
      set(value) {
        this.$data._isVisible = value;
      },
    },
  },
  watch: {
    images() {
      this.$data._isVisible = this.images.length > 0;
    },
  },
  methods: {
    onCloseBar() {
      this.$data._isVisible = false;
    },
    onCreateList() {
      const imageIDs = this.$store.state.shareListImages.map(image => image.id);

      this.$store.dispatch(CREATE_LIST, {
        listTitle: this.listTitle,
        images: imageIDs,
      });
    },
    onRemoveImage(image) {
      this.$store.commit(REMOVE_IMAGE_FROM_LIST, { image });
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scpoped>
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

  .share-bar_close-btn,
  .share-bar_clear-btn {
    position: absolute;
    bottom: 10px;
    right: 10px;
    text-decoration: underline;
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
  $social-brand-pinterest: #c32aa3;

  @mixin social-button($brand-color, $brand-icon) {
    background: $brand-color;

    &:before {
      background: url( '../assets/#{$brand-icon}');
      content: '';
      width: 24px;
      height: 24px;
      display: inline-block;
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

      &.facebook {
        @include social-button($social-brand-facebook, 'facebook-logo_white.svg')
      }

      &.twitter {
        @include social-button($social-brand-twitter, 'twitter-logo_white.svg')
      }

      &.pinterest {
        @include social-button($social-brand-pinterest, 'pinterest-logo_white.svg')
      }
    }
  }

  .fade-enter-active, .fade-leave-active {
    transition: opacity .5s;
  }
</style>
