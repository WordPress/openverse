<template>
  <li :style="styles.container">
    <VLink
      itemprop="contentUrl"
      :title="contextSensitiveTitle"
      :href="imageLink"
      class="group relative block w-full overflow-hidden rounded-sm bg-dark-charcoal-10 text-dark-charcoal-10 focus-bold-filled"
      :aria-label="contextSensitiveTitle"
      @mousedown="sendSelectSearchResultEvent"
    >
      <figure
        itemprop="image"
        itemscope
        itemtype="https://schema.org/ImageObject"
        class="absolute w-full rounded-sm"
        :class="{ 'relative aspect-square': isSquare }"
        :style="styles.figure"
      >
        <img
          ref="img"
          loading="lazy"
          class="block w-full rounded-sm object-cover duration-200 motion-safe:transition-[filter,transform]"
          :class="[
            isSquare ? 'h-full' : 'margin-auto',
            { 'scale-150 blur-image': shouldBlur },
          ]"
          :alt="
            shouldBlur
              ? $t('sensitiveContent.title.image').toString()
              : image.title
          "
          :src="imageUrl"
          :width="imgWidth"
          :height="imgHeight"
          itemprop="thumbnailUrl"
          @load="getImgDimension"
          @error="onImageLoadError($event)"
        />
        <figcaption
          class="invisible absolute bottom-0 left-0 bg-white p-1 text-dark-charcoal group-hover:visible group-focus:visible"
        >
          <h2 class="sr-only">
            {{
              shouldBlur
                ? $t("sensitiveContent.title.image").toString()
                : image.title
            }}
          </h2>
          <VLicense :license="image.license" :hide-name="true" />
        </figcaption>
      </figure>
      <i v-if="!isSquare" :style="styles.iPadding" class="block" aria-hidden />
    </VLink>
  </li>
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import type { AspectRatio, ImageDetail } from "~/types/media"
import { useImageCellSize } from "~/composables/use-image-cell-size"
import { useI18n } from "~/composables/use-i18n"
import { useAnalytics } from "~/composables/use-analytics"
import { useUiStore } from "~/stores/ui"

import { IMAGE } from "~/constants/media"

import VLicense from "~/components/VLicense/VLicense.vue"
import VLink from "~/components/VLink.vue"

import errorImage from "~/assets/image_not_available_placeholder.png"

const toAbsolutePath = (url: string, prefix = "https://") => {
  if (url.indexOf("http://") >= 0 || url.indexOf("https://") >= 0) {
    return url
  }
  return `${prefix}${url}`
}

export default defineComponent({
  name: "VImageCell",
  components: { VLicense, VLink },
  props: {
    image: {
      type: Object as PropType<ImageDetail>,
      required: true,
    },
    /**
     * The search term is added to the URL to allow the user to
     * navigate back/forward to the search results page.
     */
    searchTerm: {
      type: String,
    },
    /**
     * All content view uses the square image cells, Image view
     * uses the image's intrinsic size.
     */
    aspectRatio: {
      type: String as PropType<AspectRatio>,
      default: "square",
    },
    relatedTo: {
      type: [String, null] as PropType<string | null>,
      default: null,
    },
  },
  setup(props) {
    const isSquare = computed(() => props.aspectRatio === "square")
    const { imgHeight, imgWidth, isPanorama, styles } = useImageCellSize({
      imageSize: { width: props.image.width, height: props.image.height },
      isSquare,
    })
    const i18n = useI18n()

    const imageUrl = computed(() => {
      // TODO: check if we have blurry panorama thumbnails
      // fix for blurry panorama thumbnails, introduced in
      // https://github.com/cc-archive/cccatalog-frontend/commit/4c9bdac5
      if (isPanorama.value) {
        return toAbsolutePath(props.image.url)
      }
      const url = props.image.thumbnail || props.image.url
      return toAbsolutePath(url)
    })

    const imageLink = computed(() => {
      return `/image/${props.image.id}/${
        props.searchTerm ? "?q=" + props.searchTerm : ""
      }`
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
      element.src =
        element.src === props.image.url ? errorImage : props.image.url
    }
    /**
     * If the image is not square, on the image load event, update
     * the img's height and width with image natural dimensions.
     * @param event - the load event.
     */
    const getImgDimension = (event: Event) => {
      if (props.aspectRatio === "square") return
      const element = event.target as HTMLImageElement
      imgHeight.value = element.naturalHeight
      imgWidth.value = element.naturalWidth
    }

    const contextSensitiveTitle = computed(() => {
      return shouldBlur.value
        ? i18n.t("sensitiveContent.title.image")
        : i18n.t("browsePage.aria.imageTitle", {
            title: props.image.title,
          })
    })

    const { sendCustomEvent } = useAnalytics()
    const sendSelectSearchResultEvent = () => {
      sendCustomEvent("SELECT_SEARCH_RESULT", {
        id: props.image.id,
        mediaType: IMAGE,
        provider: props.image.provider,
        query: props.searchTerm || "",
        relatedTo: props.relatedTo,
      })
    }

    const uiStore = useUiStore()
    const shouldBlur = computed(
      () => uiStore.shouldBlurSensitive && props.image.isSensitive
    )

    return {
      styles,
      imgWidth,
      imgHeight,
      imageUrl,
      imageLink,
      contextSensitiveTitle,
      shouldBlur,

      getImageForeignUrl,
      onImageLoadError,
      getImgDimension,

      isSquare,

      sendSelectSearchResultEvent,
    }
  },
})
</script>
