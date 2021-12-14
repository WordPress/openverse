<template>
  <ImageGrid
    :images="mediaResults.items"
    :can-load-more="canLoadMore"
    :fetch-state="fetchState"
    @load-more="onLoadMore"
  />
</template>

<script>
import { propTypes } from '~/pages/search/search-page.types'
import { defineComponent } from '@nuxtjs/composition-api'
import { useLoadMore } from '~/composables/use-load-more'

const ImageSearch = defineComponent({
  name: 'ImageSearch',
  props: propTypes,
  setup(props) {
    const { canLoadMore, onLoadMore } = useLoadMore(props)
    return { canLoadMore, onLoadMore }
  },
})

export default ImageSearch
</script>
