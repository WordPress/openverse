<template>
  <VAllResultsGrid :can-load-more="canLoadMore" @load-more="onLoadMore" />
</template>

<script lang="ts">
import { defineComponent, toRef, useMeta } from '@nuxtjs/composition-api'

import { useLoadMore } from '~/composables/use-load-more'
import { propTypes } from '~/pages/search/search-page.types'

import VAllResultsGrid from '~/components/VAllResultsGrid/VAllResultsGrid.vue'

export default defineComponent({
  name: 'SearchIndex',
  components: { VAllResultsGrid },
  props: propTypes,
  setup(props) {
    useMeta({ title: `${props.searchTerm} | Openverse` })

    const searchTermRef = toRef(props, 'searchTerm')
    const { canLoadMore, onLoadMore } = useLoadMore(searchTermRef)

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
</script>
