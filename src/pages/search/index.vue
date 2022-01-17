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

import ImageGrid from '~/components/ImageGrid/ImageGrid.vue'

const SearchIndex = defineComponent({
  name: 'SearchIndex',
  components: { ImageGrid },
  props: propTypes,

  setup(props) {
    const { canLoadMore, onLoadMore } = useLoadMore(props)
    return { canLoadMore, onLoadMore }
  },
})
export default SearchIndex
</script>
