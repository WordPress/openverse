<template>
  <div :aria-label="$t('photo-details.aria.main')">
    <photo-details
      :image="image"
      :breadCrumbURL="breadCrumbURL"
      :shouldShowBreadcrumb="shouldShowBreadcrumb"
      :query="query"
      :imageWidth="imageWidth"
      :imageHeight="imageHeight"
      :imageType="imageType"
      :socialSharingEnabled="socialSharingEnabled"
      @onImageLoaded="onImageLoaded"
    />
    <div class="padding-normal margin-vertical-big">
      <photo-tags :tags="tags" :showHeader="true" />
    </div>
    <aside
      role="complementary"
      :aria-label="$t('photo-details.aria.related')"
      class="padding-normal margin-vertical-big"
    >
      <related-images
        :relatedImages="relatedImages"
        :imagesCount="imagesCount"
        :query="query"
        :filter="filter"
        :isPrimaryImageLoaded="isPrimaryImageLoaded"
      />
    </aside>
  </div>
</template>

<script>
import axios from 'axios'
import { mapActions, mapMutations, mapState } from 'vuex'
import featureFlags from '../../src/featureFlags'
import { FETCH_IMAGE, FETCH_RELATED_IMAGES } from '../../src/store/action-types'
import { SET_IMAGE } from '../../src/store/mutation-types'

const PhotoDetailPage = {
  name: 'photo-detail-page',
  props: {
    id: {
      type: String,
      default: '',
    },
  },
  data: () => ({
    breadCrumbURL: '',
    hasClarifaiTags: false,
    imagecountseparator: 'of',
    isPrimaryImageLoaded: false,
    shouldShowBreadcrumb: false,
    imageWidth: 0,
    imageHeight: 0,
    imageType: 'Unknown',
    socialSharingEnabled: featureFlags.socialSharing,
  }),
  computed: mapState({
    relatedImages: 'relatedImages',
    filter: 'query.filter',
    images: 'images',
    imagesCount: 'imagesCount',
    query: 'query',
    tags: 'image.tags',
    image: 'image',
  }),
  watch: {
    image() {
      this.getRelatedImages()
    },
  },
  beforeRouteUpdate(to, from, next) {
    this.resetImageOnRouteChanged()
    this.loadImage(to.params.id)
    next()
  },
  beforeRouteLeave(to, from, next) {
    this.resetImageOnRouteChanged()
    next()
  },
  beforeRouteEnter(to, from, nextPage) {
    nextPage((_this) => {
      if (from.path === '/search' || from.path === '/search/image') {
        _this.shouldShowBreadcrumb = true
        _this.breadCrumbURL = from.fullPath
      }
    })
  },
  methods: {
    ...mapActions([FETCH_RELATED_IMAGES, FETCH_IMAGE]),
    ...mapMutations([SET_IMAGE]),
    resetImageOnRouteChanged() {
      this.imageHeight = 0
      this.imageWidth = 0
      this.SET_IMAGE({ image: {} })
    },
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
        this.FETCH_RELATED_IMAGES({ id: this.image.id })
      }
    },
    loadImage(id) {
      return this.FETCH_IMAGE({ id })
    },
  },
  mounted() {
    if (!this.$store.state.image.id) {
      return this.loadImage(this.$route.params.id)
    }
    return this.getRelatedImages()
  },
  serverPrefetch() {
    return this.loadImage(this.$route.params.id)
  },
}

export default PhotoDetailPage
</script>
