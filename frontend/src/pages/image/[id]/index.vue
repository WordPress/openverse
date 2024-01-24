<template>
  <main :id="skipToContentTargetId" tabindex="-1" class="relative flex-grow">
    <VErrorSection
      v-if="fetchingError"
      :fetching-error="fetchingError"
      class="px-6 py-10 lg:px-10"
    />
    <template v-else-if="image">
      <VSafetyWall v-if="isHidden" :media="image" @reveal="reveal" />
      <template v-else>
        <VSingleResultControls :media="image" />
        <figure
          class="relative mb-4 grid grid-cols-1 grid-rows-1 justify-items-center border-b border-dark-charcoal-20 px-6"
        >
          <VBone
            v-if="isLoadingThumbnail"
            class="col-span-full row-span-full h-[500px] w-[500px] self-center"
          />
          <!--
              re: disabled static element interactions rule https://github.com/WordPress/openverse/issues/2906
              Note: this one, I believe, should remain disabled ; but should be double checked by the issue nonetheless
            -->
          <!-- eslint-disable-next-line vuejs-accessibility/no-static-element-interactions -->
          <img
            v-if="!sketchFabUid"
            id="main-image"
            :src="imageSrc"
            :alt="image.title"
            class="col-span-full row-span-full h-full max-h-[500px] w-full rounded-se-sm rounded-ss-sm object-contain"
            :width="imageWidth"
            :height="imageHeight"
            @load="onImageLoaded"
            @error="onImageError"
            @contextmenu="handleRightClick"
          />
          <VSketchFabViewer
            v-if="sketchFabUid"
            :uid="sketchFabUid"
            class="mx-auto rounded-se-sm rounded-ss-sm"
            @failure="sketchFabfailure = true"
          />
        </figure>

        <section
          v-if="isAdditionalSearchView"
          class="grid grid-cols-1 grid-rows-[auto,1fr] sm:grid-cols-[1fr,auto] sm:grid-rows-1 sm:gap-x-6"
        >
          <VMediaInfo :media="image" class="min-w-0 sm:col-start-1" />
          <VGetMediaButton
            :media="image"
            media-type="image"
            class="row-start-1 mb-4 !w-full flex-initial sm:col-start-2 sm:mb-0 sm:mt-1 sm:!w-auto"
          />
        </section>
        <VImageTitleButton v-else :image="image" />

        <VMediaReuse :media="image" />
        <VMediaDetails
          :media="image"
          :image-width="imageWidth"
          :image-height="imageHeight"
          :image-type="imageType"
        />
        <VRelatedImages :media-id="image.id" />
      </template>
    </template>

    <VBone
      v-else-if="isLoadingThumbnail"
      class="col-span-full row-span-full mx-auto h-[500px] w-[500px]"
    />
  </main>
</template>

<script setup lang="ts">
import {
  definePageMeta,
  firstParam,
  handledClientSide,
  isClient,
  showError,
  useAsyncData,
  useHead,
  useRoute,
} from "#imports"

import { computed, onMounted, ref, watch } from "vue"

import axios from "axios"

import { IMAGE } from "~/constants/media"
import { skipToContentTargetId } from "~/constants/window"
import type { ImageDetail } from "~/types/media"
import { useAnalytics } from "~/composables/use-analytics"
import { useSensitiveMedia } from "~/composables/use-sensitive-media"
import { useSingleResultPageMeta } from "~/composables/use-single-result-page-meta"

import { useFeatureFlagStore } from "~/stores/feature-flag"
import { useSingleResultStore } from "~/stores/media/single-result"
import { singleResultMiddleware } from "~/middleware/single-result"

import { validateUUID } from "~/utils/query-utils"

import VBone from "~/components/VSkeleton/VBone.vue"
import VMediaReuse from "~/components/VMediaInfo/VMediaReuse.vue"
import VRelatedImages from "~/components/VImageDetails/VRelatedImages.vue"
import VSketchFabViewer from "~/components/VSketchFabViewer.vue"
import VSafetyWall from "~/components/VSafetyWall/VSafetyWall.vue"
import VSingleResultControls from "~/components/VSingleResultControls.vue"
import VMediaDetails from "~/components/VMediaInfo/VMediaDetails.vue"
import VGetMediaButton from "~/components/VMediaInfo/VGetMediaButton.vue"
import VMediaInfo from "~/components/VMediaInfo/VMediaInfo.vue"
import VErrorSection from "~/components/VErrorSection/VErrorSection.vue"
import VImageTitleButton from "~/components/VMediaInfo/VImageTitleButton.vue"

import errorImage from "~/assets/image_not_available_placeholder.png"

definePageMeta({
  layout: "content-layout",
  middleware: singleResultMiddleware,
})
const singleResultStore = useSingleResultStore()

const route = useRoute()

const image = ref<ImageDetail | null>(singleResultStore.image)
const fetchingError = computed(() => singleResultStore.fetchState.fetchingError)

/**
 * To make sure that image is loaded fast, we `src` to `image.thumbnail`,
 * and replace it with the provider image once the thumbnail is loaded.
 */
const imageSrc = ref(image.value?.thumbnail)

const isLoadingThumbnail = ref(true)
const imageId = computed(() => firstParam(route.params.id))

onMounted(() => {
  isLoadingThumbnail.value = false
  imageSrc.value = image.value?.url ?? errorImage
})

const { error } = await useAsyncData(
  "single-image",
  async () => {
    if (imageId.value && validateUUID(imageId.value)) {
      const fetchedImage = await singleResultStore.fetch(IMAGE, imageId.value)
      image.value = fetchedImage
      imageSrc.value = fetchedImage.thumbnail
      return fetchedImage
    } else {
      throw new Error("Image ID not found")
    }
  },
  {
    immediate: true,
    lazy: isClient,
    watch: [imageId],
  }
)

watch(
  error,
  () => {
    if (
      (fetchingError.value && !handledClientSide(fetchingError.value)) ||
      error.value
    ) {
      showError({
        ...(fetchingError.value ?? {}),
        fatal: true,
      })
    }
  },
  { immediate: true }
)
const extractFiletype = (url: string): string | null => {
  const splitUrl = url.split(".")
  if (splitUrl.length > 1) {
    const possibleFiletype = splitUrl[splitUrl.length - 1]
    if (
      ["jpg", "jpeg", "png", "gif", "tiff", "svg"].includes(possibleFiletype)
    ) {
      return possibleFiletype
    }
  }
  return null
}
const getFiletype = (image: ImageDetail) => {
  return image.filetype ?? extractFiletype(image.url) ?? "Unknown"
}

const imageWidth = ref(image.value?.width ?? 0)
const imageHeight = ref(image.value?.height ?? 0)
const imageType = ref(image.value ? getFiletype(image.value) : "Unknown")
const isLoadingMainImage = ref(true)
const sketchFabfailure = ref(false)

const sketchFabUid = computed(() => {
  if (image.value?.source !== "sketchfab" || sketchFabfailure.value) {
    return null
  }
  return image.value.url
    .split("https://media.sketchfab.com/models/")[1]
    .split("/")[0]
})

const fetchFiletype = async (url: string) => {
  const response = await axios.head(url)
  const contentType = response.headers["content-type"]
  if (contentType?.includes("image")) {
    return contentType.split("/")[1]
  }
  return null
}

/**
 * On image error, fall back on image thumbnail or the error image.
 * @param event - image load error event.
 */
const onImageError = (event: Event) => {
  if (!(event.target instanceof HTMLImageElement)) {
    return
  }
  imageSrc.value =
    event.target.src === image.value?.url ? image.value.thumbnail : errorImage
}
/**
 * When the load event is fired for the thumbnail image, we set the dimensions
 * of the image, and replace the image src attribute with the `image.url`
 * to load the original provider image.
 * @param event - the image load event.
 */
const onImageLoaded = async (event: Event) => {
  if (!(event.target instanceof HTMLImageElement) || !image.value) {
    return
  }

  isLoadingThumbnail.value = false

  if (isLoadingMainImage.value && event.target.src === image.value.thumbnail) {
    imageWidth.value = image.value.width || event.target.naturalWidth
    imageHeight.value = image.value.height || event.target.naturalHeight
    if (imageType.value === "Unknown") {
      imageType.value =
        extractFiletype(image.value.url) ||
        (await fetchFiletype(image.value.url)) ||
        "Unknown"
    }

    imageSrc.value = image.value.url
    isLoadingMainImage.value = false
  }
}

const { sendCustomEvent } = useAnalytics()

const handleRightClick = () => {
  if (!image.value) {
    return
  }
  sendCustomEvent("RIGHT_CLICK_IMAGE", {
    id: image.value.id,
  })
}

const { reveal, isHidden } = useSensitiveMedia(image.value)

const { pageTitle, detailPageMeta } = useSingleResultPageMeta(image)

useHead(() => ({
  ...detailPageMeta,
  title: pageTitle.value,
}))

const featureFlagStore = useFeatureFlagStore()
const isAdditionalSearchView = computed(() => {
  return featureFlagStore.isOn("additional_search_views")
})
</script>

<style scoped>
section,
aside {
  @apply mb-10 w-full px-6 md:mb-16 md:max-w-screen-lg md:px-12 lg:mx-auto lg:px-16;
}
</style>
