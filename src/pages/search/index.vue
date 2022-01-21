<template>
  <VAllResultsGrid :can-load-more="canLoadMore" @load-more="onLoadMore" />
</template>

<script>
import { propTypes } from '~/pages/search/search-page.types'
import { defineComponent } from '@nuxtjs/composition-api'
import { useLoadMore } from '~/composables/use-load-more'
import VAllResultsGrid from '~/components/VAllResultsGrid/VAllResultsGrid.vue'

const SearchIndex = defineComponent({
  name: 'SearchIndex',
  components: { VAllResultsGrid },
  props: propTypes,
  setup(props) {
    const { canLoadMore, onLoadMore } = useLoadMore(props)
    return { canLoadMore, onLoadMore }
  },
})
export default SearchIndex
</script>
