<template>
  <transition name="fade">
    <div class="share-list" v-if="isVisible"
         :style="{ left: position.x + 'px', top: position.y + 'px' }">
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
                  class="cell medium-6 large-8">
              <div class="input-group">
                <input class="input-group-field"
                  type="text"
                  placeholder="Create your list"
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
      </div>
    </div>
  </transition>
</template>

<script>
import {
  ADD_IMAGE_TO_LIST,
  CREATE_LIST,
  FETCH_LISTS,
} from '@/store/action-types';

import {
  SELECT_IMAGE_FOR_LIST,
  SET_SHARE_LIST_IMAGES,
} from '@/store/mutation-types';

export default {
  name: 'share-list',
  data: () => ({
    _isVisible: false,
    listTitle: '',
    position: {
      x: 0,
      y: 0,
    },
  }),
  beforeDestroy() {
    this.unsubscribe();
    this.removeScrollEvent();
  },
  created() {
    this.unsubscribe = this.$store.subscribe((mutation) => {
      if (mutation.type === SELECT_IMAGE_FOR_LIST) {
        if (this.isVisible === false) {
          this.$store.dispatch(FETCH_LISTS);
        }
        this.setPosition(mutation.payload.image);
        this.isVisible = true;
      }
    });
  },
  computed: {
    lists() {
      return this.$store.state.shareLists;
    },
    selectedImage() {
      return this.$store.state.selectedImage;
    },
    isVisible: {
      get() {
        return this.$data._isVisible;
      },
      set(isVisible) {
        this.$data._isVisible = isVisible;
        if (isVisible === true) {
          this.listTitle = '';
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
      this.$store.dispatch(ADD_IMAGE_TO_LIST, {
        auth: list.auth,
        selectedImageID: this.selectedImage.id,
        id: list.listID,
      });
    },
    onCloseBar() {
      this.$data._isVisible = false;
    },
    onCreateList() {
      this.$store.dispatch(CREATE_LIST, {
        listTitle: this.listTitle,
        images: this.$store.state.selectedImage,
      });
    },
    onGotoListPage(listID) {
      this.$router.push(`/lists/${listID}`);
    },
    setPosition(image) {
      const pageWidth = window.innerWidth;
      const pageHeight = window.innerHeight;
      const shareListHeight = 200;
      const shareListWidth = 350;

      let positionX = image.pageX;
      let positionY = image.pageY;

      if (positionX + shareListWidth > pageWidth) {
        positionX -= shareListWidth;
      }

      if (positionY + shareListHeight > pageHeight) {
        positionY -= shareListHeight;
      }

      this.position.x = positionX;
      this.position.y = positionY;
    },
  },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  @import '../../node_modules/foundation-sites/scss/foundation';

  .share-list {
    position: absolute;
    left: 0px;
    top: 0px;
    width: 350px;
    overflow-x: scroll;
    background-color: #fff;
    z-index: 300;
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
    min-height: 100px;

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

  .fade-enter-active {
    transition: opacity .3s;
  }

  .fade-leave-active {
    transition: opacity .1s;
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
