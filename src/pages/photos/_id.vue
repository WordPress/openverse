<template>
  <div :aria-label="$t('photo-details.aria.main')">
    <PhotoDetails
      :image="image"
      :thumbnail="thumbnailURL"
      :bread-crumb-u-r-l="breadCrumbURL"
      :should-show-breadcrumb="shouldShowBreadcrumb"
      :query="query"
      :image-width="imageWidth"
      :image-height="imageHeight"
      :image-type="imageType"
      :social-sharing-enabled="socialSharingEnabled"
      @onImageLoaded="onImageLoaded"
    />
    <div class="p-4 my-6">
      <PhotoTags :tags="tags" :show-header="true" />
    </div>
    <RelatedImages
      :related-images="relatedImages"
      :images-count="relatedImagesCount"
      :query="query"
      :filter="filter"
      :is-primary-image-loaded="isPrimaryImageLoaded"
    />
  </div>
</template>

<script>
import axios from 'axios'
import { mapActions, mapMutations, mapState } from 'vuex'
import featureFlags from '~/feature-flags'
import { FETCH_IMAGE, FETCH_RELATED_MEDIA } from '~/constants/action-types'
import { SET_IMAGE, SET_RELATED_MEDIA } from '~/constants/mutation-types'
import { IMAGE } from '~/constants/media'

const PhotoDetailPage = {
  name: 'PhotoDetailPage',
  layout({ store }) {
    return store.state.isEmbedded
      ? 'embedded-with-nav-search'
      : 'with-nav-search'
  },
  props: {
    id: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      breadCrumbURL: '',
      hasClarifaiTags: false,
      isPrimaryImageLoaded: false,
      shouldShowBreadcrumb: false,
      imageWidth: 0,
      imageHeight: 0,
      imageType: 'Unknown',
      socialSharingEnabled: featureFlags.socialSharing,
    }
  },
  computed: {
    ...mapState({
      filter: (state) => state.query.filter,
      images: (state) => state.images,
      query: (state) => state.query,
      tags: (state) => state.image.tags,
      image: (state) => state.image,
    }),
    ...mapState({
      relatedImagesCount: (state) => state.images.length,
      relatedImages: (state) => state.images,
    }),
  },
  watch: {
    image() {
      this.getRelatedImages()
    },
  },
  async asyncData({ env, route }) {
    return { thumbnailURL: `${env.apiUrl}thumbs/${route.params.id}` }
  },
  async fetch({ store, route, error, app }) {
    // Clear related images if present
    if (store.state.related.images && store.state.related.images.length > 0) {
      await store.dispatch(SET_RELATED_MEDIA, {
        mediaType: IMAGE,
        relatedMedia: [],
      })
    }
    try {
      // Load the image + related images in parallel
      await Promise.all([
        store.dispatch(FETCH_IMAGE, { id: route.params.id }),
        store.dispatch(FETCH_RELATED_MEDIA, {
          mediaType: IMAGE,
          id: route.params.id,
        }),
      ])
    } catch (err) {
      error({
        statusCode: 404,
        message: app.i18n.t('error.image-not-found', { id: route.params.id }),
      })
    }
  },
  beforeRouteEnter(to, from, nextPage) {
    nextPage((_this) => {
      if (from.path === '/search/' || from.path === '/search/image') {
        _this.shouldShowBreadcrumb = true
        _this.breadCrumbURL = from.fullPath
      }
    })
  },
  methods: {
    ...mapActions([FETCH_RELATED_MEDIA]),
    ...mapActions([FETCH_IMAGE]),
    ...mapMutations([SET_IMAGE]),
    onImageLoaded(event) {
      this.imageWidth = event.target.naturalWidth
      this.imageHeight = event.target.naturalHeight
      this.isPrimaryImageLoaded = true
      axios.head(event.target.src).then((res) => {
        this.imageType = res.headers['content-type']
      })
    },
    getRelatedImages() {
      if (this.image && this.image.id) {
        this[FETCH_RELATED_MEDIA]({ mediaType: IMAGE, id: this.image.id })
      }
    },
  },
}

export default PhotoDetailPage
</script>
