<script setup lang="ts">
import { useI18n, useNuxtApp } from "#imports"

import { computed } from "vue"

import type { AspectRatio, ImageDetail } from "~/types/media"
import type { SingleResultProps } from "~/types/collection-component-props"
import { useImageCellSize } from "~/composables/use-image-cell-size"
import { useSensitiveMedia } from "~/composables/use-sensitive-media"

import { IMAGE } from "~/constants/media"

import { useSearchStore } from "~/stores/search"

import VIcon from "~/components/VIcon/VIcon.vue"
import VLicense from "~/components/VLicense/VLicense.vue"
import VLink from "~/components/VLink.vue"

import errorImage from "~/assets/image_not_available_placeholder.png"

const props = withDefaults(
  defineProps<
    SingleResultProps & {
      image: ImageDetail
      /**
       * All content view uses the square image cells, Image view
       * uses the image's intrinsic size.
       */
      aspectRatio?: AspectRatio
    }
  >(),
  {
    aspectRatio: "square",
    kind: "search",
    relatedTo: "null",
  }
)

const toAbsolutePath = (url: string, prefix = "https://") => {
  if (
    url.startsWith("http://") ||
    url.startsWith("https://") ||
    url === "/openverse-default.jpg"
  ) {
    return url
  }
  return `${prefix}${url}`
}

const isSquare = computed(() => props.aspectRatio === "square")
const { imgHeight, imgWidth, isPanorama, styles } = useImageCellSize({
  imageSize: { width: props.image.width, height: props.image.height },
  isSquare,
})
const { t } = useI18n({ useScope: "global" })

const imageUrl = computed(() => {
  // TODO: check if we have blurry panorama thumbnails
  // Use the main image file and not the thumbnails for panorama images to
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

/**
 * If the thumbnail fails to load, try replacing it with the original image URL.
 * If the original image fails, too, use the error image placeholder.
 * @param event - the error event.
 */
const onImageLoadError = (event: Event) => {
  const element = event.target as HTMLImageElement
  element.src = element.src === props.image.url ? errorImage : props.image.url
}
/**
 * If the image is not square, on the image load event, update
 * the img's height and width with image natural dimensions.
 * @param event - the load event.
 */
const getImgDimension = (event: Event) => {
  if (props.aspectRatio === "square") {
    return
  }
  const element = event.target as HTMLImageElement
  imgHeight.value = element.naturalHeight
  imgWidth.value = element.naturalWidth
}

const contextSensitiveTitle = computed(() => {
  return shouldBlur.value
    ? t("sensitiveContent.title.image")
    : t("browsePage.aria.imageTitle", {
        title: props.image.title,
      })
})

const { $sendCustomEvent } = useNuxtApp()
const searchStore = useSearchStore()

/**
 * If the user left-clicks on a search result, send
 * the SELECT_SEARCH_RESULT custom event
 * @param event - the mouse click event
 */
const sendSelectSearchResultEvent = (event: MouseEvent) => {
  if (event.button !== 0) {
    return
  }

  $sendCustomEvent("SELECT_SEARCH_RESULT", {
    id: props.image.id,
    kind: props.kind,
    mediaType: IMAGE,
    provider: props.image.provider,
    query: props.searchTerm || "",
    relatedTo: props.relatedTo ?? "null",
    sensitivities: props.image.sensitivity?.join(",") ?? "",
    isBlurred: shouldBlur.value ?? "null",
    collectionType:
      searchStore.strategy !== "default" ? searchStore.strategy : "null",
    collectionValue: searchStore.collectionValue ?? "null",
  })
}

const { isHidden: shouldBlur } = useSensitiveMedia(props.image)
</script>

<template>
  <li
    :style="styles"
    class="container w-full max-w-full"
    :class="isSquare ? 'square' : 'intrinsic'"
  >
    <VLink
      itemprop="contentUrl"
      :title="contextSensitiveTitle"
      :href="imageLink"
      class="group relative block w-full overflow-hidden rounded-sm text-gray-2 hover:no-underline focus-visible:outline-3 focus-visible:outline-offset-4"
      :aria-label="contextSensitiveTitle"
      @mousedown="sendSelectSearchResultEvent"
    >
      <figure
        itemprop="image"
        itemscope
        itemtype="https://schema.org/ImageObject"
        class="grid w-full rounded-sm"
        :class="{ 'aspect-square': isSquare }"
      >
        <img
          loading="lazy"
          class="image col-span-full row-span-full block w-full overflow-hidden rounded-sm object-cover"
          :class="[isSquare ? 'h-full' : 'margin-auto']"
          :alt="
            shouldBlur ? `${$t('sensitiveContent.title.image')}` : image.title
          "
          :src="imageUrl"
          :width="imgWidth"
          :height="imgHeight"
          itemprop="thumbnailUrl"
          @load="getImgDimension"
          @error="onImageLoadError($event)"
        />
        <span
          class="col-span-full row-span-full flex items-center justify-center bg-blur text-default backdrop-blur-xl duration-200 motion-safe:transition-opacity"
          :class="shouldBlur ? 'opacity-100' : 'opacity-0'"
          data-testid="blur-overlay"
          aria-hidden="true"
        >
          <VIcon name="eye-closed" />
        </span>
        <figcaption
          class="z-10 col-span-full my-2 self-end justify-self-start rounded-sm text-default group-hover:visible group-focus-visible:visible"
          :class="[
            isSquare
              ? 'invisible row-span-full p-2'
              : 'sm:invisible sm:row-span-full sm:p-2',
            shouldBlur ? 'sm:w-full sm:text-center' : 'bg-default',
            !shouldBlur && (isSquare ? 'mx-2' : 'sm:mx-2'),
          ]"
        >
          <h2 class="sr-only">
            {{
              shouldBlur ? `${$t("sensitiveContent.title.image")}` : image.title
            }}
          </h2>
          <div
            class="label-regular leading-none text-secondary group-hover:text-default group-focus-visible:text-default sm:text-default"
          >
            <template v-if="shouldBlur">
              {{ $t("sensitiveContent.singleResult.title") }}
            </template>
            <VLicense v-else :license="image.license" :hide-name="true" />
          </div>
        </figcaption>
      </figure>
    </VLink>
  </li>
</template>

<style scoped>
@screen sm {
  .intrinsic.container {
    flex-grow: var(--container-grow);
    width: var(--container-width);
  }
  .intrinsic .image {
    aspect-ratio: var(--img-aspect-ratio);
  }
}
</style>
