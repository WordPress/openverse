<template>
  <VLink
    itemprop="contentUrl"
    :title="image.title"
    :href="'/image/' + image.id"
    class="group block focus:ring-[3px] focus:ring-pink focus:ring-offset-[3px] focus:outline-none rounded-sm"
  >
    <figure
      itemprop="image"
      itemscope=""
      itemtype="https://schema.org/ImageObject"
      class="aspect-square relative rounded-sm"
    >
      <img
        ref="img"
        class="w-full h-full object-cover rounded-sm bg-dark-charcoal-10 text-dark-charcoal-10"
        loading="lazy"
        :alt="image.title"
        :src="getImageUrl(image)"
        :width="250"
        :height="250"
        itemprop="thumbnailUrl"
        @error="onImageLoadError($event, image)"
      />
      <figcaption
        class="absolute left-0 bottom-0 invisible group-hover:visible group-focus:visible bg-white p-1 text-dark-charcoal"
      >
        <span class="sr-only">{{ image.title }}</span>
        <VLicense :license="image.license" :hide-name="true" />
      </figcaption>
    </figure>
  </VLink>
</template>

<script>
import VLink from '~/components/VLink.vue'
import VLicense from '~/components/VLicense/VLicense.vue'

// eslint-disable-next-line @typescript-eslint/no-var-requires
const errorImage = require('~/assets/image_not_available_placeholder.png')

const toAbsolutePath = (url, prefix = 'https://') => {
  if (url.indexOf('http://') >= 0 || url.indexOf('https://') >= 0) {
    return url
  }
  return `${prefix}${url}`
}

export default {
  name: 'VImageCell',
  components: { VLink, VLicense },
  props: ['image'],
  methods: {
    getImageUrl(image) {
      if (!image) return ''
      const url = image.thumbnail || image.url
      return toAbsolutePath(url)
    },
    getImageForeignUrl(image) {
      return toAbsolutePath(image.foreign_landing_url)
    },
    onImageLoadError(event, image) {
      const element = event.target
      if (element.src !== image.url) {
        element.src = image.url
      } else {
        element.src = errorImage
      }
    },
    onFocusLeave(event) {
      this.$emit('focus-leave', event)
    },
  },
}
</script>
