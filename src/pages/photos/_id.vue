<template>
  <div :aria-label="$t('photo-details.aria.main')">
    <PhotoDetails
      :image="image"
      :thumbnail="thumbnailURL"
      :bread-crumb-u-r-l="breadCrumbURL"
      :should-show-breadcrumb="shouldShowBreadcrumb"
      :image-width="imageWidth"
      :image-height="imageHeight"
      :image-type="imageType"
      @onImageLoaded="onImageLoaded"
    />
    <RelatedImages :image-id="imageId" />
  </div>
</template>

<script>
import axios from 'axios'
import { mapActions, mapState } from 'vuex'
import { FETCH_IMAGE } from '~/constants/action-types'
import { SEARCH } from '~/constants/store-modules'

const PhotoDetailPage = {
  name: 'PhotoDetailPage',
  layout({ store }) {
    return store.state.nav.isEmbedded
      ? 'embedded-with-nav-search'
      : 'with-nav-search'
  },
  data() {
    return {
      breadCrumbURL: '',
      isPrimaryImageLoaded: false,
      shouldShowBreadcrumb: false,
      imageWidth: 0,
      imageHeight: 0,
      imageType: 'Unknown',
      thumbnailURL: '',
      imageId: null,
    }
  },
  computed: {
    ...mapState(SEARCH, ['image']),
  },
  async asyncData({ env, route }) {
    return {
      thumbnailURL: `${env.apiUrl}thumbs/${route.params.id}`,
      imageId: route.params.id,
    }
  },
  async fetch() {
    this.imageId = this.$route.params.id
    this.thumbnailURL = `${process.env.apiUrl}thumbs/${this.imageId}`

    try {
      await this.fetchImage({ id: this.imageId })
    } catch (err) {
      const errorMessage = this.$t('error.image-not-found', {
        id: this.imageId,
      })
      this.$nuxt.error({
        statusCode: 404,
        message: errorMessage,
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
    ...mapActions(SEARCH, { fetchImage: FETCH_IMAGE }),
    onImageLoaded(event) {
      this.imageWidth = event.target.naturalWidth
      this.imageHeight = event.target.naturalHeight
      this.isPrimaryImageLoaded = true
      axios.head(event.target.src).then((res) => {
        this.imageType = res.headers['content-type']
      })
    },
  },
}

export default PhotoDetailPage
</script>
