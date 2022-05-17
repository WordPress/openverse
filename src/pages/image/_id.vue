<template>
  <div>
    <figure class="w-full mb-4 pt-12 px-6 bg-dark-charcoal-06 relative">
      <div
        v-if="backToSearchPath"
        class="absolute left-0 top-0 right-0 w-full px-2"
      >
        <VBackToSearchResultsLink :path="backToSearchPath" />
      </div>

      <img
        v-if="!sketchFabUid"
        id="main-image"
        :src="isLoadingFullImage ? image.thumbnail : image.url"
        :alt="image.title"
        class="h-full w-full max-h-[500px] mx-auto rounded-t-sm object-contain"
        :width="imageWidth"
        :height="imageHeight"
        @load="onImageLoaded"
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
      class="flex flex-row md:flex-row-reverse flex-wrap justify-between md:mt-6"
    >
      <VButton
        as="VLink"
        :href="image.foreign_landing_url"
        class="btn-main flex-initial w-full md:w-max mb-4 md:mb-0"
        size="large"
        >{{ $t('image-details.weblink') }}</VButton
      >
      <span class="flex-1 flex flex-col justify-center">
        <h1 class="text-base md:text-3xl font-semibold leading-[130%]">
          {{ image.title }}
        </h1>
        <i18n
          v-if="image.creator"
          path="image-details.creator"
          tag="span"
          class="font-semibold leading-[130%]"
        >
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
      </span>
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
import { useSingleResultStore } from '~/stores/media/single-result'
import { useRelatedMediaStore } from '~/stores/media/related-media'
import type { ImageDetail } from '~/models/media'
import { createDetailPageMeta } from '~/utils/og'

import VButton from '~/components/VButton.vue'
import VLink from '~/components/VLink.vue'
import VImageDetails from '~/components/VImageDetails/VImageDetails.vue'
import VMediaReuse from '~/components/VMediaInfo/VMediaReuse.vue'
import VRelatedImages from '~/components/VImageDetails/VRelatedImages.vue'
import VSketchFabViewer from '~/components/VSketchFabViewer.vue'
import VBackToSearchResultsLink from '~/components/VBackToSearchResultsLink.vue'

export default defineComponent({
  name: 'VImageDetailsPage',
  components: {
    VButton,
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
    const isLoadingFullImage = ref(true)
    const sketchFabfailure = ref(false)

    const sketchFabUid = computed(() => {
      if (image.value?.source !== 'sketchfab' || sketchFabfailure.value) {
        return null
      }
      return image.value.url
        .split('https://media.sketchfab.com/models/')[1]
        .split('/')[0]
    })

    const onImageLoaded = (event: Event) => {
      if (!(event.target instanceof HTMLImageElement)) {
        return
      }
      imageWidth.value = image.value?.width || event.target.naturalWidth
      imageHeight.value = image.value?.height || event.target.naturalHeight
      if (image.value?.filetype) {
        imageType.value = image.value.filetype
      } else {
        if (event.target) {
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
      }
      isLoadingFullImage.value = false
    }

    return {
      image,
      relatedMedia,
      relatedFetchState,
      imageWidth,
      imageHeight,
      imageType,
      isLoadingFullImage,
      sketchFabfailure,
      sketchFabUid,
      onImageLoaded,
      backToSearchPath,
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
  @apply w-full px-6 md:px-16 mb-10 md:mb-16 md:max-w-screen-lg lg:mx-auto;
}

.btn-main {
  @apply py-3 md:py-4 md:px-6 text-sr md:text-2xl font-semibold;
}
</style>
