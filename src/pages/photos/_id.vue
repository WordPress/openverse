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
    <PhotoTags :tags="tags" :show-header="true" class="p-4 my-6" />
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
import { RELATED } from '~/constants/store-modules'

const PhotoDetailPage = {
  name: 'PhotoDetailPage',
  layout({ store }) {
    return store.state.nav.isEmbedded
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
    ...mapState(['images', 'query', 'image']),
    filter() {
      return this.query.filter
    },
    tags() {
      return this.image.tags
    },
    relatedImages() {
      return this.$store.state.related.images
    },
    relatedImagesCount() {
      return this.relatedImages.length
    },
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
      store.commit(`${RELATED}/${SET_RELATED_MEDIA}`, {
        mediaType: IMAGE,
        relatedMedia: [],
      })
    }
    try {
      // Load the image + related images in parallel
      await Promise.all([
        store.dispatch(`${FETCH_IMAGE}`, { id: route.params.id }),
        store.dispatch(`${RELATED}/${FETCH_RELATED_MEDIA}`, {
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
    ...mapActions({ fetchRelatedMedia: `${RELATED}/${FETCH_RELATED_MEDIA}` }),
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
        this.fetchRelatedMedia({ mediaType: IMAGE, id: this.image.id })
      }
    },
  },
}

export default PhotoDetailPage
</script>
