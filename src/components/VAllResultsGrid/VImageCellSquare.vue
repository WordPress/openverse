<template>
  <VLink
    itemprop="contentUrl"
    :title="image.title"
    :href="'/image/' + image.id"
    class="group block rounded-sm focus:outline-none focus:ring-[3px] focus:ring-pink focus:ring-offset-[3px]"
  >
    <figure
      itemprop="image"
      itemscope
      itemtype="https://schema.org/ImageObject"
      class="relative aspect-square rounded-sm"
    >
      <img
        ref="img"
        class="h-full w-full rounded-sm bg-dark-charcoal-10 object-cover text-dark-charcoal-10"
        loading="lazy"
        :alt="image.title"
        :src="getImageUrl()"
        :width="250"
        :height="250"
        itemprop="thumbnailUrl"
        @error="onImageLoadError($event)"
      />
      <figcaption
        class="invisible absolute left-0 bottom-0 bg-white p-1 text-dark-charcoal group-hover:visible group-focus:visible"
      >
        <span class="sr-only">{{ image.title }}</span>
        <VLicense :license="image.license" :hide-name="true" />
      </figcaption>
    </figure>
  </VLink>
</template>

<script lang="ts">
import { defineComponent, PropType } from '@nuxtjs/composition-api'

import type { ImageDetail } from '~/models/media'

import VLink from '~/components/VLink.vue'
import VLicense from '~/components/VLicense/VLicense.vue'

import errorImage from '~/assets/image_not_available_placeholder.png'

const toAbsolutePath = (url: string, prefix = 'https://') => {
  if (url.indexOf('http://') >= 0 || url.indexOf('https://') >= 0) {
    return url
  }
  return `${prefix}${url}`
}

export default defineComponent({
  name: 'VImageCell',
  components: { VLink, VLicense },
  props: {
    image: {
      type: Object as PropType<ImageDetail>,
      required: true,
    },
  },
  setup(props) {
    const getImageUrl = () => {
      if (!props.image) return ''
      const url = props.image.thumbnail || props.image.url
      return toAbsolutePath(url)
    }
    const getImageForeignUrl = () =>
      toAbsolutePath(props.image.foreign_landing_url)

    const onImageLoadError = (event: Event) => {
      const element = event.target as HTMLImageElement
      if (element.src !== props.image.url) {
        element.src = props.image.url
      } else {
        element.src = errorImage
      }
    }
    return {
      getImageUrl,
      getImageForeignUrl,
      onImageLoadError,
    }
  },
})
</script>
