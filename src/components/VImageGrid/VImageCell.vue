<template>
  <VLink
    :href="'/image/' + image.id"
    class="w-full block group relative overflow-hidden rounded-sm focus:ring-[3px] focus:ring-pink focus:ring-offset-[3px] focus:outline-none bg-dark-charcoal-10 text-dark-charcoal-10"
    :aria-label="image.title"
    :style="containerStyle"
    @keydown.native.shift.tab.exact="$emit('shift-tab', $event)"
  >
    <figure class="absolute w-full" :style="figureStyle">
      <img
        ref="img"
        loading="lazy"
        class="margin-auto block w-full"
        :alt="image.title"
        :src="imageUrl"
        :width="imgWidth"
        :height="imgHeight"
        @load="getImgDimension"
        @error="onImageLoadError($event)"
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

<script lang="ts">
import {
  computed,
  defineComponent,
  PropType,
  ref,
} from '@nuxtjs/composition-api'

import type { ImageDetail } from '~/models/media'

import VLicense from '~/components/VLicense/VLicense.vue'
import VLink from '~/components/VLink.vue'

import errorImage from '~/assets/image_not_available_placeholder.png'

const minAspect = 3 / 4
const maxAspect = 16 / 9
const panoramaAspect = 21 / 9
const minRowWidth = 450
const widthBasis = minRowWidth / maxAspect

const toAbsolutePath = (url: string, prefix = 'https://') => {
  if (url.indexOf('http://') >= 0 || url.indexOf('https://') >= 0) {
    return url
  }
  return `${prefix}${url}`
}

export default defineComponent({
  name: 'VImageCell',
  components: { VLicense, VLink },
  props: {
    image: {
      type: Object as PropType<ImageDetail>,
      required: true,
    },
  },
  setup(props) {
    const imgHeight = ref(props.image.height || 100)
    const imgWidth = ref(props.image.width || 100)

    const imageAspect = computed(() => imgWidth.value / imgHeight.value)

    const containerAspect = computed(() => {
      if (imageAspect.value > maxAspect) return maxAspect
      if (imageAspect.value < minAspect) return minAspect
      return imageAspect.value
    })
    const iPadding = computed(() => {
      if (imageAspect.value < minAspect) return (1 / minAspect) * 100
      if (imageAspect.value > maxAspect) return (1 / maxAspect) * 100
      return (1 / imageAspect.value) * 100
    })
    const imageWidth = computed(() => {
      if (imageAspect.value < maxAspect) return 100
      return (imageAspect.value / maxAspect) * 100
    })
    const imageTop = computed(() => {
      if (imageAspect.value > minAspect) return 0
      return (
        ((minAspect - imageAspect.value) /
          (imageAspect.value * minAspect * minAspect)) *
        -50
      )
    })
    const imageLeft = computed(() => {
      if (imageAspect.value < maxAspect) return 0
      return ((imageAspect.value - maxAspect) / maxAspect) * -50
    })

    const imageUrl = computed(() => {
      // TODO: check if we have blurry panorama thumbnails
      // fix for blurry panorama thumbnails, introduced in
      // https://github.com/cc-archive/cccatalog-frontend/commit/4c9bdac5
      if (imageAspect.value > panoramaAspect)
        return toAbsolutePath(props.image.url)
      const url = props.image.thumbnail || props.image.url
      return toAbsolutePath(url)
    })

    const getImageForeignUrl = () =>
      toAbsolutePath(props.image.foreign_landing_url)

    /**
     * If the thumbnail fails to load, try replacing it with the original image URL.
     * If the original image fails, too, use the error image placeholder.
     * @param event - the error event.
     */
    const onImageLoadError = (event: Event) => {
      const element = event.target as HTMLImageElement
      if (element.src !== props.image.url) {
        element.src = props.image.url
      } else {
        element.src = errorImage
      }
    }
    const getImgDimension = (event: Event) => {
      const element = event.target as HTMLImageElement
      imgHeight.value = element.naturalHeight
      imgWidth.value = element.naturalWidth
    }

    const containerStyle = computed(() => {
      const containerWidth = containerAspect.value * widthBasis
      return `width: ${containerWidth}px;flex-grow: ${containerWidth}`
    })

    const figureStyle = computed(
      () =>
        `width: ${imageWidth.value}%; top: ${imageTop.value}%; left:${imageLeft.value}%;`
    )

    return {
      imgHeight,
      imgWidth,
      containerStyle,
      figureStyle,
      iPadding,
      imageUrl,

      getImageForeignUrl,
      onImageLoadError,
      getImgDimension,
    }
  },
})
</script>
