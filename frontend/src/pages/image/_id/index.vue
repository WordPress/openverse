<template>
  <main :id="skipToContentTargetId" tabindex="-1">
    <div v-if="backToSearchPath" class="w-full px-2 py-2 md:px-6">
      <VBackToSearchResultsLink
        :id="$route.params.id"
        :href="backToSearchPath"
      />
    </div>

    <figure
      class="relative mb-4 grid grid-cols-1 grid-rows-1 justify-items-center border-b border-dark-charcoal-20 px-6"
    >
      <VBone
        v-if="isLoadingThumbnail"
        class="col-span-full row-span-full h-[500px] w-[500px] self-center"
      />
      <img
        v-if="image && !sketchFabUid"
        id="main-image"
        :src="imageSrc"
        :alt="image.title"
        class="col-span-full row-span-full h-full max-h-[500px] w-full rounded-se-sm rounded-ss-sm object-contain"
        :width="imageWidth"
        :height="imageHeight"
        @load="onImageLoaded"
        @error="onImageError"
        @contextmenu="handleRightClick($route.params.id)"
      />
      <VSketchFabViewer
        v-if="sketchFabUid"
        :uid="sketchFabUid"
        class="mx-auto rounded-se-sm rounded-ss-sm"
        @failure="sketchFabfailure = true"
      />
    </figure>

    <template v-if="image">
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
          :send-external-link-click-event="false"
          @click="sendGetMediaEvent"
        >
          {{ $t("imageDetails.weblink") }}
        </VButton>
        <div class="description-bold flex flex-1 flex-col justify-center">
          <h1 class="description-bold md:heading-5 line-clamp-2">
            {{ image.title }}
          </h1>
          <i18n v-if="image.creator" path="imageDetails.creator" tag="span">
            <template #name>
              <VLink
                v-if="image.creator_url"
                :aria-label="
                  $t('mediaDetails.aria.creatorUrl', {
                    creator: image.creator,
                  })
                "
                :href="image.creator_url"
                :send-external-link-click-event="false"
                @click="sendVisitCreatorLinkEvent"
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
      <VRelatedImages />
    </template>
  </main>
</template>

<script lang="ts">
import axios from "axios"

import { computed, ref } from "vue"
import {
  defineComponent,
  useContext,
  useFetch,
  useMeta,
  useRoute,
} from "@nuxtjs/composition-api"

import { IMAGE } from "~/constants/media"
import { skipToContentTargetId } from "~/constants/window"
import type { ImageDetail } from "~/types/media"
import { useAnalytics } from "~/composables/use-analytics"

import { useSingleResultStore } from "~/stores/media/single-result"
import { useSearchStore } from "~/stores/search"
import { createDetailPageMeta } from "~/utils/og"
import { singleResultMiddleware } from "~/middleware/single-result"

import VBackToSearchResultsLink from "~/components/VBackToSearchResultsLink.vue"
import VBone from "~/components/VSkeleton/VBone.vue"
import VButton from "~/components/VButton.vue"
import VImageDetails from "~/components/VImageDetails/VImageDetails.vue"
import VLink from "~/components/VLink.vue"
import VMediaReuse from "~/components/VMediaInfo/VMediaReuse.vue"
import VRelatedImages from "~/components/VImageDetails/VRelatedImages.vue"
import VSketchFabViewer from "~/components/VSketchFabViewer.vue"

import errorImage from "~/assets/image_not_available_placeholder.png"

export default defineComponent({
  name: "VImageDetailsPage",
  components: {
    VBone,
    VBackToSearchResultsLink,
    VButton,
    VLink,
    VImageDetails,
    VMediaReuse,
    VRelatedImages,
    VSketchFabViewer,
  },
  layout: "content-layout",
  middleware: singleResultMiddleware,
  // Fetching on the server is disabled because it is
  // handled by the `singleResultMiddleware`.
  fetchOnServer: false,
  setup() {
    const singleResultStore = useSingleResultStore()
    const searchStore = useSearchStore()

    const route = useRoute()

    const image = ref<ImageDetail | null>(singleResultStore.image)

    /**
     * To make sure that image is loaded fast, we `src` to `image.thumbnail`,
     * and replace it with the provider image once the thumbnail is loaded.
     */
    const imageSrc = ref(image.value?.thumbnail)

    const isLoadingThumbnail = ref(true)

    const { error: nuxtError } = useContext()

    useFetch(async () => {
      const imageId = route.value.params.id
      const fetchedImage = await singleResultStore.fetch(IMAGE, imageId)
      if (!fetchedImage) {
        nuxtError(singleResultStore.fetchState.fetchingError ?? {})
      } else {
        image.value = fetchedImage
        imageSrc.value = fetchedImage.thumbnail
      }
    })

    const backToSearchPath = computed(() => searchStore.backToSearchPath)

    const imageWidth = ref(image.value?.width ?? 0)
    const imageHeight = ref(image.value?.height ?? 0)
    const imageType = ref(image.value?.filetype ?? "Unknown")
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
        event.target.src === image.value?.url
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
      if (!(event.target instanceof HTMLImageElement) || !image.value) return

      isLoadingThumbnail.value = false

      if (isLoadingMainImage.value) {
        imageWidth.value = image.value.width || event.target.naturalWidth
        imageHeight.value = image.value.height || event.target.naturalHeight

        if (image.value.filetype) {
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

    const handleRightClick = (id: string) => {
      sendCustomEvent("RIGHT_CLICK_IMAGE", {
        id,
      })
    }

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

    const sendVisitCreatorLinkEvent = () => {
      if (!image.value) {
        return
      }
      sendCustomEvent("VISIT_CREATOR_LINK", {
        id: image.value.id,
        url: image.value.creator_url ?? "",
      })
    }

    useMeta(createDetailPageMeta(image.value?.title, image.value?.url))

    return {
      image,
      imageWidth,
      imageHeight,
      imageSrc,
      imageType,
      sketchFabfailure,
      sketchFabUid,

      isLoadingThumbnail,
      onImageLoaded,
      onImageError,
      handleRightClick,
      backToSearchPath,

      skipToContentTargetId,

      sendGetMediaEvent,
      sendVisitCreatorLinkEvent,
    }
  },
  head: {},
})
</script>

<style scoped>
section,
aside {
  @apply mb-10 w-full px-6 md:mb-16 md:max-w-screen-lg md:px-12 lg:mx-auto lg:px-16;
}
</style>
