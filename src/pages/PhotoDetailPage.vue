<template>
  <div class="photo-detail-page">
    <header-section showNavSearch="true" />
    <main role="main" :aria-label="$t('photo-details.aria.main')">
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
    </main>
    <footer-section></footer-section>
  </div>
</template>

<script>
import axios from 'axios'
import PhotoDetails from '@/components/ImageDetails/PhotoDetails'
import PhotoTags from '@/components/PhotoTags'
import RelatedImages from '@/components/RelatedImages'
import HeaderSection from '@/components/HeaderSection'
import FooterSection from '@/components/FooterSection'
import featureFlags from '@/featureFlags'
import { mapActions, mapMutations, mapState } from 'vuex'
import { FETCH_IMAGE, FETCH_RELATED_IMAGES } from '@/store/action-types'
import { SET_IMAGE } from '@/store/mutation-types'

const PhotoDetailPage = {
  name: 'photo-detail-page',
  props: {
    id: {
      type: String,
      default: '',
    },
  },
  components: {
    HeaderSection,
    RelatedImages,
    FooterSection,
    PhotoDetails,
    PhotoTags,
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
    // this is called when users navigate to this page.
    // To avoid having previously loaded image being displayed,
    // this resets the image data and then load the actual image that
    // is supposed to be displayed.
    this.resetImageOnRouteChanged()
    this.loadImage(to.params.id)
    next()
  },
  beforeRouteLeave(to, from, next) {
    // this resets the image once the user navigates away from the page
    this.resetImageOnRouteChanged()
    next()
  },
  beforeRouteEnter(to, from, nextPage) {
    // sets the internal value shouldShowBreadcrumb so that the
    // "back to search results" link is rendered with the correct link
    // to the results page the user was before.

    nextPage((_this) => {
      if (from.path === '/search' || from.path === '/search/image') {
        _this.shouldShowBreadcrumb = true // eslint-disable-line no-param-reassign
        _this.breadCrumbURL = from.fullPath // eslint-disable-line no-param-reassign
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
      // Make a HEAD request to get the image content-type header
      // @todo: Should probably refactor this, just seems too trival to warrant it's own service or class
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
