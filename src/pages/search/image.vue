<template>
  <ImageGrid
    :images="results"
    :can-load-more="canLoadMore"
    :fetch-state="fetchState"
    @load-more="onLoadMore"
  />
</template>

<script>
import { propTypes } from '~/pages/search/search-page.types'
import { computed, defineComponent } from '@nuxtjs/composition-api'
import { useLoadMore } from '~/composables/use-load-more'

const ImageSearch = defineComponent({
  name: 'ImageSearch',
  props: propTypes,
  setup(props) {
    const results = computed(() =>
      Object.values(props.mediaResults?.image?.items ?? [])
    )
    const { canLoadMore, onLoadMore } = useLoadMore(props)
    return { canLoadMore, onLoadMore, results }
  },
})

export default ImageSearch
</script>
