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
            @contextmenu="handleRightClick($route.params.id)"
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
        <section
          v-else
          id="title-button"
          class="flex flex-row flex-wrap justify-between gap-x-6 md:mt-6 md:flex-row-reverse"
        >
          <VGetMediaButton
            :media="image"
            media-type="image"
            class="mb-4 !w-full flex-initial md:mb-0 md:!w-max"
          />
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
        <VMediaDetails
          :media="image"
          :image-width="imageWidth"
          :image-height="imageHeight"
          :image-type="imageType"
        />
        <VRelatedImages />
      </template>
    </template>
    <VBone
      v-else-if="isLoadingThumbnail"
      class="col-span-full row-span-full h-[500px] w-[500px] self-center"
    />
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

import { IMAGE, isAdditionalSearchType } from "~/constants/media"
import { skipToContentTargetId } from "~/constants/window"
import type { ImageDetail } from "~/types/media"
import { useAnalytics } from "~/composables/use-analytics"
import { useSensitiveMedia } from "~/composables/use-sensitive-media"
import { useSingleResultPageMeta } from "~/composables/use-single-result-page-meta"

import { isRetriable } from "~/utils/errors"
import { useSingleResultStore } from "~/stores/media/single-result"
import { singleResultMiddleware } from "~/middleware/single-result"

import { useFeatureFlagStore } from "~/stores/feature-flag"

import { useProviderStore } from "~/stores/provider"

import VBone from "~/components/VSkeleton/VBone.vue"
import VLink from "~/components/VLink.vue"
import VMediaReuse from "~/components/VMediaInfo/VMediaReuse.vue"
import VRelatedImages from "~/components/VImageDetails/VRelatedImages.vue"
import VSketchFabViewer from "~/components/VSketchFabViewer.vue"
import VSafetyWall from "~/components/VSafetyWall/VSafetyWall.vue"
import VSingleResultControls from "~/components/VSingleResultControls.vue"
import VMediaDetails from "~/components/VMediaInfo/VMediaDetails.vue"
import VGetMediaButton from "~/components/VMediaInfo/VGetMediaButton.vue"
import VMediaInfo from "~/components/VMediaInfo/VMediaInfo.vue"

import errorImage from "~/assets/image_not_available_placeholder.png"

export default defineComponent({
  name: "VImageDetailsPage",
  components: {
    VMediaInfo,
    VGetMediaButton,
    VMediaDetails,
    VSingleResultControls,
    VSafetyWall,
    VBone,
    VLink,
    VMediaReuse,
    VRelatedImages,
    VSketchFabViewer,
  },
  layout: "content-layout",
  middleware: singleResultMiddleware,
  setup() {
    const singleResultStore = useSingleResultStore()

    const route = useRoute()

    const image = ref<ImageDetail | null>(singleResultStore.image)
    const fetchingError = computed(
      () => singleResultStore.fetchState.fetchingError
    )

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
        if (fetchingError.value && !isRetriable(fetchingError.value)) {
          nuxtError(fetchingError.value)
        }
      } else {
        image.value = fetchedImage
        imageSrc.value = fetchedImage.thumbnail
      }
    })

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
        source: image.value.source ?? image.value.provider,
        url: image.value.creator_url ?? "",
      })
    }

    const { reveal, hide, isHidden } = useSensitiveMedia(image.value)

    const { pageTitle, detailPageMeta } = useSingleResultPageMeta(image)

    useMeta(() => ({
      ...detailPageMeta,
      title: pageTitle.value,
    }))

    const featureFlagStore = useFeatureFlagStore()

    const isAdditionalSearchView = computed(() => {
      return featureFlagStore.isOn("additional_search_views")
    })
    const providerStore = useProviderStore()
    const sourceName = computed(() => {
      return image.value
        ? providerStore.getProviderName(
            image.value.source ?? image.value.provider,
            "image"
          )
        : ""
    })

    return {
      isAdditionalSearchView,
      sourceName,

      image,
      fetchingError,
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

      skipToContentTargetId,

      sendGetMediaEvent,
      sendVisitCreatorLinkEvent,

      isHidden,
      reveal,
      hide,
    }
  },
  // Necessary for useMeta
  head: {},
  methods: { isAdditionalSearchType },
  // Fetching on the server is disabled because it is
  // handled by the `singleResultMiddleware`.
  fetchOnServer: false,
})
</script>

<style scoped>
section,
aside {
  @apply mb-10 w-full px-6 md:mb-16 md:max-w-screen-lg md:px-12 lg:mx-auto lg:px-16;
}
</style>
