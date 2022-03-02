<template>
  <VImageGrid
    :images="results"
    :can-load-more="canLoadMore"
    :fetch-state="fetchState"
    @load-more="onLoadMore"
  />
</template>

<script>
import { computed, defineComponent, useMeta } from '@nuxtjs/composition-api'

import { propTypes } from '~/pages/search/search-page.types'
import { useLoadMore } from '~/composables/use-load-more'

const ImageSearch = defineComponent({
  name: 'ImageSearch',
  props: propTypes,
  setup(props) {
    useMeta({ title: `${props.searchTerm} | Openverse` })

    const results = computed(() =>
      Object.values(props.mediaResults?.image?.items ?? [])
    )
    const { canLoadMore, onLoadMore } = useLoadMore(props)
    return { canLoadMore, onLoadMore, results }
  },
  head: {},
})

export default ImageSearch
</script>
