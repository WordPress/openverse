<template>
  <div>
    <figure class="relative mb-4 w-full bg-dark-charcoal-06 px-6 pt-12">
      <div
        v-if="backToSearchPath"
        class="absolute left-0 top-0 right-0 w-full px-2"
      >
        <VBackToSearchResultsLink :path="backToSearchPath" />
      </div>

      <img
        v-if="!sketchFabUid"
        id="main-image"
        :src="imageSrc"
        :alt="image.title"
        class="mx-auto h-full max-h-[500px] w-full rounded-t-sm object-contain"
        :width="imageWidth"
        :height="imageHeight"
        @load="onImageLoaded"
        @error="onImageError"
      />
      <VSketchFabViewer
        v-if="sketchFabUid"
        :uid="sketchFabUid"
        class="mx-auto rounded-t-sm"
        @failure="sketchFabfailure = true"
      />
    </figure>

    <section
      id="title-button"
      class="flex flex-row flex-wrap justify-between md:mt-6 md:flex-row-reverse"
    >
      <VButton
        as="VLink"
        :href="image.foreign_landing_url"
        class="btn-main mb-4 w-full flex-initial leading-[1.3] md:mb-0 md:w-max"
        size="large"
      >
        {{ $t('image-details.weblink') }}
        <VIcon
          :icon-path="externalIcon"
          :rtl-flip="true"
          class="ms-2 md:h-6 md:w-6"
          :size="4"
        />
      </VButton>
      <div
        class="flex flex-1 flex-col justify-center text-base font-semibold leading-[1.3]"
      >
        <h1 class="font-semibold md:text-3xl">
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
    <VRelatedImages :media="relatedMedia" :fetch-state="relatedFetchState" />
  </div>
</template>

<script lang="ts">
import axios from 'axios'

import {
  computed,
  defineComponent,
  ref,
  useRoute,
} from '@nuxtjs/composition-api'

import { IMAGE } from '~/constants/media'
import type { ImageDetail } from '~/models/media'
import { useSingleResultStore } from '~/stores/media/single-result'
import { useRelatedMediaStore } from '~/stores/media/related-media'
import { createDetailPageMeta } from '~/utils/og'

import VButton from '~/components/VButton.vue'
import VIcon from '~/components/VIcon/VIcon.vue'
import VLink from '~/components/VLink.vue'
import VImageDetails from '~/components/VImageDetails/VImageDetails.vue'
import VMediaReuse from '~/components/VMediaInfo/VMediaReuse.vue'
import VRelatedImages from '~/components/VImageDetails/VRelatedImages.vue'
import VSketchFabViewer from '~/components/VSketchFabViewer.vue'
import VBackToSearchResultsLink from '~/components/VBackToSearchResultsLink.vue'

import errorImage from '~/assets/image_not_available_placeholder.png'
import externalIcon from '~/assets/icons/external-link.svg'

export default defineComponent({
  name: 'VImageDetailsPage',
  components: {
    VButton,
    VIcon,
    VLink,
    VImageDetails,
    VMediaReuse,
    VRelatedImages,
    VSketchFabViewer,
    VBackToSearchResultsLink,
  },
  beforeRouteEnter(to, from, next) {
    if (from.path.includes('/search/')) {
      to.meta.backToSearchPath = from.fullPath
    }
    next()
  },
  setup() {
    const route = useRoute()

    const singleResultStore = useSingleResultStore()
    const relatedMediaStore = useRelatedMediaStore()
    const image = computed(() =>
      singleResultStore.mediaType === IMAGE
        ? (singleResultStore.mediaItem as ImageDetail)
        : null
    )

    const backToSearchPath = computed(() => route.value.meta?.backToSearchPath)
    const relatedMedia = computed(() => relatedMediaStore.media)
    const relatedFetchState = computed(() => relatedMediaStore.fetchState)

    const imageWidth = ref(0)
    const imageHeight = ref(0)
    const imageType = ref('Unknown')
    /**
     * To make sure that image is loaded fast, we `src` to `image.thumbnail`,
     * and then replace it with the provider image once it is loaded.
     */
    const imageSrc = ref(image.value.thumbnail)
    const isLoadingMainImage = ref(true)
    const sketchFabfailure = ref(false)

    const sketchFabUid = computed(() => {
      if (image.value?.source !== 'sketchfab' || sketchFabfailure.value) {
        return null
      }
      return image.value.url
        .split('https://media.sketchfab.com/models/')[1]
        .split('/')[0]
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
              imageType.value = res.headers['content-type']
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
    return {
      image,
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
      backToSearchPath,
      externalIcon,
    }
  },
  async asyncData({ app, error, route, $pinia }) {
    const imageId = route.params.id
    const singleResultStore = useSingleResultStore($pinia)
    try {
      await singleResultStore.fetch(IMAGE, imageId)
    } catch (err) {
      const errorMessage = app.i18n
        .t('error.image-not-found', {
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
  @apply mb-10 w-full px-6 md:mb-16 md:max-w-screen-lg md:px-16 lg:mx-auto;
}

.btn-main {
  @apply py-3 text-sr font-semibold md:py-4 md:px-6 md:text-2xl;
}
</style>
