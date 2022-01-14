<template>
  <div :aria-label="$t('photo-details.aria.main')">
    <VPhotoDetails
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
import { MEDIA } from '~/constants/store-modules'
import RelatedImages from '~/components/ImageDetails/RelatedImages.vue'
import VPhotoDetails from '~/components/ImageDetails/VPhotoDetails.vue'

const PhotoDetailPage = {
  name: 'PhotoDetailPage',
  components: { RelatedImages, VPhotoDetails },
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
    ...mapState(MEDIA, ['image']),
  },
  async asyncData({ env, route }) {
    return {
      thumbnailURL: `${env.apiUrl}images/${route.params.id}/thumb/`,
      imageId: route.params.id,
    }
  },
  async fetch() {
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
    ...mapActions(MEDIA, { fetchImage: FETCH_IMAGE }),
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
