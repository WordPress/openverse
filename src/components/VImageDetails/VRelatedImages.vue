<template>
  <aside>
    <h3 class="text-2xl md:text-3xl mb-6">
      {{ $t('image-details.related-images') }}
    </h3>
    <!-- TODO: use a image grid with correct margins and items gaps -->
    <ImageGrid
      :images="images"
      :can-load-more="false"
      :fetch-state="{
        isFetching: $fetchState.pending,
        fetchingError: $fetchState.error,
      }"
    />
  </aside>
</template>

<script>
import { ref } from '@nuxtjs/composition-api'
import useRelated from '~/composables/use-related'
import { IMAGE } from '~/constants/media'
import ImageGrid from '~/components/ImageGrid/ImageGrid.vue'

export default {
  name: 'VRelatedImages',
  components: { ImageGrid },
  props: {
    imageId: {
      type: String,
      required: true,
    },
    service: {},
  },
  setup(props) {
    const mainImageId = ref(props.imageId)
    const relatedOptions = {
      mediaType: IMAGE,
      mediaId: mainImageId,
    }
    // Using service prop to be able to mock when testing
    if (props.service) {
      relatedOptions.service = props.service
    }
    /**
     * Fetches related images on `imageId` change.
     */
    const { media: images } = useRelated(relatedOptions)

    return { images }
  },
}
</script>
