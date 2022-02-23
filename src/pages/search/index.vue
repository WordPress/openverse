<template>
  <VAllResultsGrid :can-load-more="canLoadMore" @load-more="onLoadMore" />
</template>

<script>
import { propTypes } from '~/pages/search/search-page.types'
import {
  useMeta,
  useStore,
  defineComponent,
  computed,
} from '@nuxtjs/composition-api'
import { useLoadMore } from '~/composables/use-load-more'
import VAllResultsGrid from '~/components/VAllResultsGrid/VAllResultsGrid.vue'

const SearchIndex = defineComponent({
  name: 'SearchIndex',
  components: { VAllResultsGrid },
  props: propTypes,
  setup(props) {
    const store = useStore()

    const query = computed(() => store.state.search.query.q)
    useMeta({ title: `${query.value} | Openverse` })

    const { canLoadMore, onLoadMore } = useLoadMore(props)
    return { canLoadMore, onLoadMore }
  },
  head: {
    meta: [
      {
        hid: 'robots',
        name: 'robots',
        content: 'noindex',
      },
    ],
  },
})
export default SearchIndex
</script>
