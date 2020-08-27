<template>
  <div
    :aria-label="image.title"
    class="search-grid_item-container"
    :style="`width: ${containerAspect * widthBasis}px;
    flex-grow: ${containerAspect * widthBasis}`"
  >
    <figure class="search-grid_item">
      <i :style="`padding-bottom:${iPadding}%`"></i>
      <router-link
        :to="'/photos/' + image.id"
        @click="onGotoDetailPage($event, image)"
        class="search-grid_image-ctr"
        :style="`width: ${imageWidth}%; top: ${imageTop}%; left:${imageLeft}%;`"
      >
        <img
          ref="img"
          :class="{
            'search-grid_image': true,
            'search-grid_image__fill': !shouldContainImage,
          }"
          :alt="image.title"
          :src="getImageUrl(image)"
          @load="getImgDimension"
          @error="onImageLoadError($event, image)"
        />
      </router-link>
      <figcaption class="overlay overlay__top padding-small">
        <license-icons :license="image.license"></license-icons>
      </figcaption>
      <figcaption
        class="overlay overlay__bottom padding-vertical-small padding-horizontal-normal"
      >
        <span class="caption has-text-weight-semibold">{{ image.title }}</span>
      </figcaption>
    </figure>
  </div>
</template>

<script>
import LicenseIcons from './LicenseIcons'
import getProviderLogo from '../src/utils/getProviderLogo'

const errorImage = require('../assets/image_not_available_placeholder.png')

const minAspect = 3 / 4
const maxAspect = 16 / 9
const panaromaAspect = 21 / 9
const minRowWidth = 450

const toAbsolutePath = (url, prefix = 'https://') => {
  if (url.indexOf('http://') >= 0 || url.indexOf('https://') >= 0) {
    return url
  }
  return `${prefix}${url}`
}

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
    }
  },
  computed: {
    imageAspect() {
      return this.imgWidth / this.imgHeight
    },
    containerAspect() {
      if (this.imageAspect > maxAspect) return maxAspect
      if (this.imageAspect < minAspect) return minAspect
      return this.imageAspect
    },
    iPadding() {
      if (this.imageAspect < minAspect) return (1 / minAspect) * 100
      if (this.imageAspect > maxAspect) return (1 / maxAspect) * 100
      return (1 / this.imageAspect) * 100
    },
    imageWidth() {
      if (this.imageAspect < maxAspect) return 100
      return (this.imageAspect / maxAspect) * 100
    },
    imageTop() {
      if (this.imageAspect > minAspect) return 0
      return (
        ((minAspect - this.imageAspect) /
          (this.imageAspect * minAspect * minAspect)) *
        -50
      )
    },
    imageLeft() {
      if (this.imageAspect < maxAspect) return 0
      return ((this.imageAspect - maxAspect) / maxAspect) * -50
    },
  },
  methods: {
    getImageUrl(image) {
      if (!image) {
        return ''
      }
      const url = image.thumbnail || image.url
      // fix for blurry panaroma thumbnails
      if (this.imageAspect > panaromaAspect) return toAbsolutePath(url)
      return toAbsolutePath(url)
    },
    getImageForeignUrl(image) {
      return toAbsolutePath(image.foreign_landing_url)
    },
    getProviderLogo(providerName) {
      return getProviderLogo(providerName)
    },
    onGotoDetailPage(event, image) {
      // doesn't use router to redirect to photo details page in case the user
      // has the Command (Mac) or Ctrl Key (Windows) pressed, so that they can
      // open the page on a new tab with either of those keys pressed.
      if (!event.metaKey && !event.ctrlKey) {
        event.preventDefault()
        this.$router.push({
          name: 'photo-detail-page',
          params: { id: image.id, location: window.scrollY },
        })
      }
    },
    onImageLoadError(event, image) {
      const element = event.target
      if (element.src !== image.url) {
        element.src = image.url
      } else {
        element.src = errorImage
      }
    },
    getImgDimension(e) {
      this.imgHeight = e.target.naturalHeight
      this.imgWidth = e.target.naturalWidth
    },
  },
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style lang="scss" scoped>
.search-grid_image-ctr {
  background: #ebece4;
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

  &:hover .overlay {
    opacity: 1;
    bottom: 0;
  }
}

.overlay {
  position: absolute;
  opacity: 0;
  transition: all 0.4s ease;
  color: #fff;
  display: block;
  top: -100%;

  &__top {
    top: 0;
    width: 100%;
    height: 2rem;
  }

  &__bottom {
    background-color: #000;
    bottom: -100%;
    top: auto;
    text-overflow: ellipsis;
    white-space: nowrap;
    overflow: hidden;
    max-width: 100%;
  }

  // Show on touch devices
  @media (hover: none) {
    position: absolute;
    opacity: 1;
    bottom: 0;
  }
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
</style>
