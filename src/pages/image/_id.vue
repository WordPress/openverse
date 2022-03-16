<template>
  <div>
    <figure class="w-full mb-4 pt-8 md:pt-12 px-6 bg-dark-charcoal-06 relative">
      <div
        v-if="showBackToSearchLink"
        class="absolute left-0 top-0 right-0 z-40 w-full px-2"
      >
        <VBackToSearchResultsLink />
      </div>

      <img
        v-if="!sketchFabUid"
        id="main-image"
        :src="isLoadingFullImage ? image.thumbnail : image.url"
        :alt="image.title"
        class="h-full max-h-[500px] mx-auto rounded-t-sm"
        @load="onImageLoaded"
      />
      <SketchFabViewer
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
    <VRelatedImages :image-id="imageId" />
  </div>
</template>

<script>
import axios from 'axios'
import { mapState } from 'vuex'

import { MEDIA } from '~/constants/store-modules'
import { FETCH_MEDIA_ITEM } from '~/constants/action-types'
import { IMAGE } from '~/constants/media'

import VButton from '~/components/VButton.vue'
import VIcon from '~/components/VIcon/VIcon.vue'
import VLink from '~/components/VLink.vue'
import VImageDetails from '~/components/VImageDetails/VImageDetails.vue'
import VMediaReuse from '~/components/VMediaInfo/VMediaReuse.vue'
import VRelatedImages from '~/components/VImageDetails/VRelatedImages.vue'
import SketchFabViewer from '~/components/SketchFabViewer.vue'
import VBackToSearchResultsLink from '~/components/VBackToSearchResultsLink.vue'

const VImageDetailsPage = {
  name: 'VImageDetailsPage',
  components: {
    VButton,
    VIcon,
    VLink,
    VImageDetails,
    VMediaReuse,
    VRelatedImages,
    SketchFabViewer,
    VBackToSearchResultsLink,
  },
  data() {
    return {
      imageWidth: 0,
      imageHeight: 0,
      imageType: 'Unknown',
      isLoadingFullImage: true,
      showBackToSearchLink: false,
      sketchFabfailure: false,
    }
  },
  computed: {
    ...mapState(MEDIA, ['image']),
    sketchFabUid() {
      if (this.image.source !== 'sketchfab' || this.sketchFabfailure) {
        return null
      }
      return this.image.url
        .split('https://media.sketchfab.com/models/')[1]
        .split('/')[0]
    },
  },
  async asyncData({ app, error, route, store }) {
    const imageId = route.params.id
    try {
      await store.dispatch(`${MEDIA}/${FETCH_MEDIA_ITEM}`, {
        id: imageId,
        mediaType: IMAGE,
      })
      return {
        imageId: imageId,
      }
    } catch (err) {
      const errorMessage = app.i18n.t('error.image-not-found', {
        id: imageId,
      })
      error({
        statusCode: 404,
        message: errorMessage,
      })
    }
  },
  beforeRouteEnter(to, from, nextPage) {
    nextPage((_this) => {
      if (
        from.name === _this.localeRoute({ path: '/search/' }).name ||
        from.name === _this.localeRoute({ path: '/search/image' }).name
      ) {
        _this.showBackToSearchLink = true
      }
    })
  },
  methods: {
    onImageLoaded(event) {
      this.imageWidth = this.image.width || event.target.naturalWidth
      this.imageHeight = this.image.height || event.target.naturalHeight
      if (this.image.filetype) {
        this.imageType = this.image.filetype
      } else {
        axios
          .head(event.target.src)
          .then((res) => {
            this.imageType = res.headers['content-type']
          })
          .catch(() => {
            /**
             * Do nothing. This avoid the console warning "Uncaught (in promise) Error:
             * Network Error" in Firefox in development mode.
             */
          })
      }
      this.isLoadingFullImage = false
    },
  },
  head() {
    const title = `${this.image.title} | Openverse`

    return {
      title,
      meta: [
        {
          hid: 'robots',
          name: 'robots',
          content: 'noindex',
        },
        {
          hid: 'og:title',
          name: 'og:title',
          content: title,
        },
        {
          hid: 'og:image',
          name: 'og:image',
          content: this.image.url,
        },
      ],
    }
  },
}

export default VImageDetailsPage
</script>

<style scoped>
section,
aside {
  @apply px-6 md:px-16 mb-10 md:mb-16 md:max-w-screen-lg lg:mx-auto;
}

.btn-main {
  @apply py-3 md:py-4 md:px-6 text-sr md:text-2xl font-semibold;
}
</style>
