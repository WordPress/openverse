<template>
<transition name="fade">
<div class="share-list" v-if="isVisible">
    <header class="share-list_header">
      <h5>ADD TO LIST</h5>
      <div class="share-list_close-btn-ctr">
        <button @click.prevent="onCloseBar"
                class="button secondary tiny share-list_close-btn">
          close
        </button>
      </div>
    </header>
    <div class="share-list_create-ctr">
      <div class="share-list_input-ctr">
        <form v-on:submit.prevent="onCreateList"
              method="post"
              class="cell medium-6 large-8"
              v-if="this.shouldShowList">
          <div class="input-group">
            <input class="input-group-field"
              type="text"
              placeholder="Name your list"
              required="required"
              v-model="listTitle">
            <div class="input-group-button">
              <input type="submit" class="share-list_create-btn button" value="Create" >
            </div>
          </div>
        </form>
      </div>
    </div>
    <div class="share-list_images-ctr grid-x">
      <h6 v-if="lists.length === 0">
        You currently don't have any saved lists. <br/> Start by creating a list.
      </h6>
      <div class="share-list_images cell large-12">
        <transition-group name="list-item" class="share-list_images-list" tag="ul">
          <li class="share-list_image-item"
              v-for="(list) in lists"
              :key="list.listID"
              @click.prevent="onAddToList(list)">
              <div class="share-list_image-ctr">
                <img class="share-list_image" :src="list.thumbnail">
              </div>
              <span class="share-list_add-label">Add to</span>
              <span class="share-list_image-label">{{ list.listID }}</span>
              <button @click.prevent="onGotoListPage(list.listID)"
                class="button success tiny share-list_view-btn">
                view
              </button>
          </li>
          </transition-group>
      </div>
      <div class="cell medium-6 large-6 grid-x">
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
        <div class="share-list_social-items cell medium-6 large-4"
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
import { CREATE_LIST, FETCH_LISTS, UPDATE_LIST } from '@/store/action-types';
import {
  SET_SHARE_LIST_IMAGES,
  SELECT_IMAGE_FOR_LIST,
} from '@/store/mutation-types';

export default {
  name: 'share-list',
  data: () => ({
    listTitle: null,
    _isVisible: false,
  }),
  created() {
    this.unsubscribe = this.$store.subscribe((mutation) => {
      if (mutation.type === SELECT_IMAGE_FOR_LIST) {
        if (this.isVisible === false) {
          this.$store.dispatch(FETCH_LISTS);
        }
        this.isVisible = true;
      }
    });
  },
  computed: {
    lists() {
      return this.$store.state.shareLists;
    },
    shareText() {
      return encodeURI(`I created an image list @creativecommons: ${this.shareListURL}`);
    },
    selectedImages() {
      return this.$store.state.selectedImages;
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
      set(isVisible) {
        this.$data._isVisible = isVisible;
        if (isVisible === true) {
          this.listTitle = null;
          this.addScrollEvent();
        } else {
          this.$store.commit(SET_SHARE_LIST_IMAGES, { shareListImages: [] });
        }
      },
    },
  },
  methods: {
    addScrollEvent() {
      window.addEventListener('scroll', this.removeScrollEvent.bind(this));
    },
    removeScrollEvent() {
      this.isVisible = false;
      window.removeEventListener('scroll', this.removeScrollEvent);
    },
    onAddToList(list) {
      this.$store.dispatch(UPDATE_LIST, {
        auth: list.auth,
        selectedImageID: this.selectedImages[0],
        id: list.listID,
      });
    },
    onCloseBar() {
      this.$data._isVisible = false;
    },
    onCreateList() {
      this.$store.dispatch(CREATE_LIST, {
        listTitle: this.listTitle,
        images: this.$store.state.selectedImages,
      });
    },
    onGotoListPage(listID) {
      this.$router.push(`/lists/${listID}`);
    },
    beforeDestroy() {
      this.unsubscribe();
      this.removeScrollEvent();
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  @import '../../node_modules/foundation-sites/scss/foundation';

  .share-list {
    position: fixed;
    right: 10px;
    bottom: 30px;
    width: 400px;
    overflow-x: scroll;
    background-color: #fff;
    z-index: 100;
    white-space: nowrap;
    border: 1px solid #E6EAEA;
    border-radius: 2px;

    .input-group {
      margin: 0;
    }
  }

  .share-list_header {
    border-bottom: 1px solid #E6EAEA;
    padding: 10px 15px 10px 15px;

    h5 {
      display: inline-block;
      font-size: .85em;
      font-weight: 600;
      letter-spacing: 1px;
      line-height: 1.25;
      width: 50%;
      margin: 0;
      vertical-align: super;
    }

    .share-list_close-btn-ctr {
      display: inline-block;
      width: 50%;
    }

    .share-list_close-btn {
      margin: 0;
      float: right;
      border-radius: 2px;
    }
  }

  .share-list_create-ctr {
    padding: 10px;
    border-bottom: 1px solid #E6EAEA;
  }

  .share-list_images-ctr {
    padding: 10px;
    min-height: 200px;

    h6 {
      width: 100%;
      text-align: center;
    }
  }

  .share-list_images-list {
    padding: 0;
    margin: 0;
    overflow-y: scroll;
    max-height: 300px;
  }

  .share-list_image-ctr {
    display: inline-block;
    min-width: 130px;
  }

  .share-list_image {
    display: inline-block;
    max-height: 50px;
  }

  .share-list_add-label {
    opacity: 0;
  }

  .share-list_image-item {
    position: relative;
    padding: 5px;
    cursor: pointer;

    &:hover {
      background: #E6EAEA;

      .share-list_add-label {
        opacity: 1;
      }
    }
  }

  .share-list_create-btn {
    border-top-right-radius: 2px !important;
    border-bottom-right-radius: 2px !important;
  }

  .share-list_image-remove-btn {
    cursor: pointer;
    width: 16px;
    height: 16px;
    display: inline-block;
    top: 2px;
    right: 5px;
    position: absolute;
    z-index: 200;
  }

  .share-list_view-btn {
    padding: 10px;
    position: absolute;
    right: 10px;
    color: #fff !important;
    border-radius: 2px;
  }

  .share-list_social-items {
    padding-left: 30px;
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

  .share-list_social-items {

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
    transition: opacity .3s;
  }

  .list-item-enter-active,
  .list-item-leave-active {
    transition: opacity 0.3s, transform 0.3s;
    transform-origin: left center;
  }

  .list-item-enter,
  .list-item-leave-to {
    opacity: 0;
    transform: scale(0.5);
  }
</style>
