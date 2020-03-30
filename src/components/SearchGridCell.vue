<template>
  <div class="search-grid_item-container"
    :style="`width: ${containerAspect * widthBasis}px;
    flex-grow: ${containerAspect * widthBasis}`">
    <figure class="search-grid_item">
      <i :style="`padding-bottom:${iPadding}%`"></i>
      <a
        :href="'/photos/' + image.id"
        @click="onGotoDetailPage($event, image)"
        class="search-grid_image-ctr"
        :style="`width: ${imageWidth}%; top: ${imageTop}%; left:${imageLeft}%;`">
        <img
          ref="img"
          :class="{'search-grid_image': true, 'search-grid_image__fill': !shouldContainImage}"
          :alt="image.title" :src="getImageUrl(image)"
          @error="onImageLoadError($event, image)">
      </a>
      <figcaption class="search-grid_item-overlay search-grid_item-overlay__top padding-top-small">
        <license-icons :image="image"></license-icons>
      </figcaption>
      <figcaption class="search-grid_item-overlay search-grid_item-overlay__bottom">
        <a class="search-grid_overlay-provider"
            :title="image.title"
            :href="getImageForeignUrl(image)"
            @click.stop="() => false"
            target="new">
            <img class="search-grid_overlay-provider-logo"
              :alt="image.source"
              :src="getProviderLogo(image.source)">
            {{ image.title }}
        </a>
      </figcaption>
    </figure>
  </div>
</template>

<script>
import LicenseIcons from '@/components/LicenseIcons';
import getProviderLogo from '@/utils/getProviderLogo';

const errorImage = require('@/assets/image_not_available_placeholder.png');

const minAspect = 3 / 4;
const maxAspect = 16 / 9;
const panaromaAspect = 21 / 9;
const minRowWidth = 450;

const toAbsolutePath = (url, prefix = 'https://') => {
  if (url.indexOf('http://') >= 0 || url.indexOf('https://') >= 0) {
    return url;
  }
  return `${prefix}${url}`;
};

export default {
  name: 'search-grid-cell',
  props: ['image', 'shouldContainImage'],
  components: {
    LicenseIcons,
  },
  data() {
    return {
      widthBasis: minRowWidth / maxAspect,
      imgHeight: this.image.height || 100,
      imgWidth: this.image.width || 100,
    };
  },
  computed: {
    imageAspect() {
      return this.imgWidth / this.imgHeight;
    },
    containerAspect() {
      if (this.imageAspect > maxAspect) return maxAspect;
      if (this.imageAspect < minAspect) return minAspect;
      return this.imageAspect;
    },
    iPadding() {
      if (this.imageAspect < minAspect) return (1 / minAspect) * 100;
      if (this.imageAspect > maxAspect) return (1 / maxAspect) * 100;
      return (1 / this.imageAspect) * 100;
    },
    imageWidth() {
      if (this.imageAspect < maxAspect) return 100;
      return (this.imageAspect / maxAspect) * 100;
    },
    imageTop() {
      if (this.imageAspect > minAspect) return 0;
      return ((minAspect - this.imageAspect) / (this.imageAspect * minAspect * minAspect)) * -50;
    },
    imageLeft() {
      if (this.imageAspect < maxAspect) return 0;
      return ((this.imageAspect - maxAspect) / maxAspect) * -50;
    },
  },
  methods: {
    getImageUrl(image) {
      if (!image) {
        return '';
      }
      const url = image.thumbnail || image.url;
      // fix for blurry panaroma thumbnails
      if (this.imageAspect > panaromaAspect) return toAbsolutePath(url);
      return toAbsolutePath(url);
    },
    getImageForeignUrl(image) {
      return toAbsolutePath(image.foreign_landing_url);
    },
    getProviderLogo(providerName) {
      return getProviderLogo(providerName);
    },
    onGotoDetailPage(event, image) {
      // doesn't use router to redirect to photo details page in case the user
      // has the Command (Mac) or Ctrl Key (Windows) pressed, so that they can
      // open the page on a new tab with either of those keys pressed.
      if (!event.metaKey && !event.ctrlKey) {
        event.preventDefault();
        this.$router.push({ name: 'photo-detail-page', params: { id: image.id, location: window.scrollY } });
      }
    },
    onImageLoadError(event, image) {
      const element = event.target;
      if (element.src !== image.url) {
        element.src = image.url;
      }
      else {
        element.src = errorImage;
      }
    },
    getImgDimension() {
      this.imgHeight = this.$refs.img.naturalHeight;
      this.imgWidth = this.$refs.img.naturalWidth;
    },
  },
  mounted() {
    if (!this.image.width) this.getImgDimension();
  },
};
</script>


<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
  .search-grid_image-ctr {
    background: #EBECE4;
    display: block;
    width: 100%;
  }

  .search-grid_item-container {
    margin: 10px;
  }

  .search-grid_item {
    position: relative;
    width: 100%;
    overflow: hidden;

    i {
      display: block;
    }

    a {
      position: absolute;
      vertical-align: bottom;
      img {
        width: 100%;
      }
    }

    &:hover .search-grid_item-overlay {
      opacity: 1;
      bottom: 0;
    }

    &:hover .search-grid_item-overlay__top {
      top: 0;
    }
  }

  .search-grid_item-overlay {
    position: absolute;
    opacity: 0;
    transition: all .4s ease;
    width: 100%;
    height: 30px;
    color: #fff;
    padding: 0 10px;
    display: block;
    top: -100%;

    &__top {
      transition: all .5s ease;
      background: linear-gradient(to bottom,
                  rgba(0,0,0,.5)
                  0,
                  rgba(0,0,0,0) 100%);
      top: 0;
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
  }

  .search-grid_overlay-provider {
    width: calc( 100% - 30px );
    display: block;
    bottom: 10px;
    left: 10px;
    color: #fff;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;

    &:hover {
      text-decoration: underline;
    }
  }

  .search-grid_overlay-provider-logo {
    max-height: 30px;
    max-width: 30px;
    vertical-align: middle;
  }

  .search-grid_item {
    width: 100%;
    position: relative;
    display: block;
    float: left;
    flex: 0 0 auto;
    flex-grow: 1;
    cursor: pointer;
  }

  .search-grid_image {
    margin: auto;
    display: block;
  }

  .search-grid_image__fill {
    width: 100%;
  }

  @media screen and (max-width: 600px) {
    .search-grid_item-overlay {
      position: absolute;
      opacity: 1;
      bottom: 0;
    }

    .search-grid_overlay-add {
      position: absolute;
      width:  44px;
      height: 44px;
      bottom: 0;
    }

     .search-grid_layout-control {
      text-align: left !important;
    }
  }
</style>
