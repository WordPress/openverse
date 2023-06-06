<template>
  <VSkipToContentContainer as="main">
    <div v-if="backToSearchPath" class="w-full px-2 py-2 md:px-6">
      <VBackToSearchResultsLink :id="image.id" :href="backToSearchPath" />
    </div>

    <figure class="relative mb-4 border-b border-dark-charcoal-20 px-6">
      <img
        v-if="!sketchFabUid"
        id="main-image"
        :src="imageSrc"
        :alt="image.title"
        class="mx-auto h-full max-h-[500px] w-full rounded-se-sm rounded-ss-sm object-contain"
        :width="imageWidth"
        :height="imageHeight"
        @load="onImageLoaded"
        @error="onImageError"
        @contextmenu="handleRightClick(image)"
      />
      <VSketchFabViewer
        v-if="sketchFabUid"
        :uid="sketchFabUid"
        class="mx-auto rounded-se-sm rounded-ss-sm"
        @failure="sketchFabfailure = true"
      />
    </figure>

    <section
      id="title-button"
      class="flex flex-row flex-wrap justify-between gap-x-6 md:mt-6 md:flex-row-reverse"
    >
      <VButton
        as="VLink"
        :href="image.foreign_landing_url"
        variant="filled-pink"
        class="description-bold mb-4 !w-full flex-initial md:mb-0 md:!w-max"
        show-external-icon
        :external-icon-size="6"
        has-icon-end
        size="large"
        @click="sendGetMediaEvent"
      >
        {{ $t("image-details.weblink") }}
      </VButton>
      <div class="description-bold flex flex-1 flex-col justify-center">
        <h1 class="description-bold md:heading-5 line-clamp-2">
          {{ image.title }}
        </h1>
        <i18n v-if="image.creator" path="image-details.creator" tag="span">
          <template #name>
            <VLink
              v-if="image.creator_url"
              :aria-label="
                $t('media-details.aria.creator-url', {
                  creator: image.creator,
                })
              "
              :href="image.creator_url"
              >{{ image.creator }}</VLink
            >
            <span v-else>{{ image.creator }}</span>
          </template>
        </i18n>
      </div>
    </section>

    <VMediaReuse :media="image" />
    <VImageDetails
      :image="image"
      :image-width="imageWidth"
      :image-height="imageHeight"
      :image-type="imageType"
    />
    <VRelatedImages
      v-if="hasRelatedMedia"
      :media="relatedMedia"
      :fetch-state="relatedFetchState"
    />
  </VSkipToContentContainer>
</template>

<script lang="ts">
import axios from "axios"

import { computed, ref } from "vue"
import { defineComponent } from "@nuxtjs/composition-api"

import { IMAGE } from "~/constants/media"
import type { ImageDetail } from "~/types/media"
import { useAnalytics } from "~/composables/use-analytics"

import { useSingleResultStore } from "~/stores/media/single-result"
import { useRelatedMediaStore } from "~/stores/media/related-media"
import { useSearchStore } from "~/stores/search"
import { createDetailPageMeta } from "~/utils/og"
import { singleResultMiddleware } from "~/middleware/single-result"

import VBackToSearchResultsLink from "~/components/VBackToSearchResultsLink.vue"
import VButton from "~/components/VButton.vue"
import VImageDetails from "~/components/VImageDetails/VImageDetails.vue"
import VLink from "~/components/VLink.vue"
import VMediaReuse from "~/components/VMediaInfo/VMediaReuse.vue"
import VRelatedImages from "~/components/VImageDetails/VRelatedImages.vue"
import VSketchFabViewer from "~/components/VSketchFabViewer.vue"
import VSkipToContentContainer from "~/components/VSkipToContentContainer.vue"

import { useAnalytics } from "~/composables/use-analytics"

import errorImage from "~/assets/image_not_available_placeholder.png"

export default defineComponent({
  name: "VImageDetailsPage",
  components: {
    VBackToSearchResultsLink,
    VButton,
    VLink,
    VImageDetails,
    VMediaReuse,
    VRelatedImages,
    VSketchFabViewer,
    VSkipToContentContainer,
  },
  layout: "content-layout",
  middleware: singleResultMiddleware,
  setup() {
    const singleResultStore = useSingleResultStore()
    const relatedMediaStore = useRelatedMediaStore()
    const searchStore = useSearchStore()

    const image = computed(() =>
      singleResultStore.mediaType === IMAGE
        ? (singleResultStore.mediaItem as ImageDetail)
        : null
    )

    const backToSearchPath = computed(() => searchStore.backToSearchPath)
    const hasRelatedMedia = computed(() => relatedMediaStore.media.length > 0)
    const relatedMedia = computed(() => relatedMediaStore.media)
    const relatedFetchState = computed(() => relatedMediaStore.fetchState)

    const imageWidth = ref(0)
    const imageHeight = ref(0)
    const imageType = ref("Unknown")
    /**
     * To make sure that image is loaded fast, we `src` to `image.thumbnail`,
     * and then replace it with the provider image once it is loaded.
     */
    const imageSrc = ref(image.value.thumbnail)
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

    /**
     * On image error, fall back on image thumbnail or the error image.
     * @param event - image load error event.
     */
    const onImageError = (event: Event) => {
      if (!(event.target instanceof HTMLImageElement)) {
        return
      }
      imageSrc.value =
        event.target.src === image.value.url
          ? image.value.thumbnail
          : errorImage
    }
    /**
     * When the load event is fired for the thumbnail image, we set the dimensions
     * of the image, and replace the image src attribute with the `image.url`
     * to load the original provider image.
     * @param event - the image load event.
     */
    const onImageLoaded = (event: Event) => {
      if (!(event.target instanceof HTMLImageElement)) {
        return
      }
      if (isLoadingMainImage.value) {
        imageWidth.value = image.value?.width || event.target.naturalWidth
        imageHeight.value = image.value?.height || event.target.naturalHeight

        if (image.value?.filetype) {
          imageType.value = image.value.filetype
        } else {
          axios
            .head(event.target.src)
            .then((res) => {
              imageType.value = res.headers["content-type"]
            })
            .catch(() => {
              /**
               * Do nothing. This avoids the console warning "Uncaught (in promise) Error:
               * Network Error" in Firefox in development mode.
               */
            })
        }
        imageSrc.value = image.value.url
        isLoadingMainImage.value = false
      }
    }

    const { sendCustomEvent } = useAnalytics()

    const handleRightClick = (image: { id: string, originalTitle: string }) => {
      sendCustomEvent("RIGHT_CLICK_IMAGE", {
        set: image.originalTitle,
        identifier: image.id,

    const sendGetMediaEvent = () => {
      if (!image.value) {
        return
      }
      sendCustomEvent("GET_MEDIA", {
        id: image.value.id,
        provider: image.value.provider,
        mediaType: IMAGE,
      })
    }

    return {
      image,
      hasRelatedMedia,
      relatedMedia,
      relatedFetchState,
      imageWidth,
      imageHeight,
      imageSrc,
      imageType,
      sketchFabfailure,
      sketchFabUid,
      onImageLoaded,
      onImageError,
      handleRightClick,
      backToSearchPath,

      sendGetMediaEvent,
    }
  },
  async asyncData({ app, error, route, $pinia }) {
    const imageId = route.params.id
    const singleResultStore = useSingleResultStore($pinia)
    try {
      await singleResultStore.fetch(IMAGE, imageId)
    } catch (err) {
      const errorMessage = app.i18n
        .t("error.image-not-found", {
          id: imageId,
        })
        .toString()
      return error({
        statusCode: 404,
        message: errorMessage,
      })
    }
  },
  head() {
    return createDetailPageMeta(this.image.title, this.image.url)
  },
})
</script>

<style scoped>
section,
aside {
  @apply mb-10 w-full px-6 md:mb-16 md:max-w-screen-lg md:px-12 lg:mx-auto lg:px-16;
}
</style>
