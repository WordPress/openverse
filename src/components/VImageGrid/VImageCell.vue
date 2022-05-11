<template>
  <VLink
    :href="'/image/' + image.id"
    class="w-full block group relative overflow-hidden rounded-sm focus:ring-[3px] focus:ring-pink focus:ring-offset-[3px] focus:outline-none bg-dark-charcoal-10 text-dark-charcoal-10"
    :aria-label="image.title"
    :style="`width: ${containerAspect * widthBasis}px;flex-grow: ${
      containerAspect * widthBasis
    }`"
    @click="onGotoDetailPage($event, image)"
    @keydown.native.shift.tab.exact="$emit('shift-tab', $event)"
  >
    <figure
      class="absolute w-full"
      :style="`width: ${imageWidth}%; top: ${imageTop}%; left:${imageLeft}%;`"
    >
      <img
        ref="img"
        loading="lazy"
        class="margin-auto block w-full"
        :alt="image.title"
        :src="getImageUrl(image)"
        :width="imgWidth"
        :height="imgHeight"
        @load="getImgDimension"
        @error="onImageLoadError($event, image)"
      />
      <figcaption
        class="absolute left-0 bottom-0 invisible group-hover:visible group-focus:visible bg-white p-1 text-dark-charcoal"
      >
        <span class="sr-only">{{ image.title }}</span>
        <VLicense :license="image.license" :hide-name="true" />
      </figcaption>
    </figure>
    <i :style="`padding-bottom:${iPadding}%`" class="block" aria-hidden />
  </VLink>
</template>

<script>
import VLicense from '~/components/VLicense/VLicense.vue'
import VLink from '~/components/VLink.vue'

// eslint-disable-next-line @typescript-eslint/no-var-requires
const errorImage = require('~/assets/image_not_available_placeholder.png')

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
  name: 'VImageCell',
  components: { VLicense, VLink },
  props: ['image'],
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
      if (this.imageAspect > panaromaAspect) return toAbsolutePath(url)
      return toAbsolutePath(url)
    },
    getImageForeignUrl(image) {
      return toAbsolutePath(image.foreign_landing_url)
    },
    onGotoDetailPage(event, image) {
      if (!event.metaKey && !event.ctrlKey) {
        event.preventDefault()
        const detailRoute = this.localeRoute({
          name: 'PhotoDetailPage',
          params: { id: image.id, location: window.scrollY },
        })
        this.$router.push(detailRoute)
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
