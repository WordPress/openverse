<template>
  <VImageGrid
    :images="results"
    :can-load-more="canLoadMore"
    :fetch-state="fetchState"
    @load-more="onLoadMore"
    @shift-tab="handleShiftTab"
  />
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  toRef,
  useMeta,
} from '@nuxtjs/composition-api'

import { propTypes } from '~/pages/search/search-page.types'
import { useLoadMore } from '~/composables/use-load-more'
import { useFocusFilters } from '~/composables/use-focus-filters'

import VImageGrid from '~/components/VImageGrid/VImageGrid.vue'

export default defineComponent({
  name: 'ImageSearch',
  components: { VImageGrid },
  props: propTypes,
  setup(props) {
    useMeta({ title: `${props.searchTerm} | Openverse` })

    const results = computed(() => props.resultItems.image)

    const searchTermRef = toRef(props, 'searchTerm')
    const { canLoadMore, onLoadMore } = useLoadMore(searchTermRef)

    const focusFilters = useFocusFilters()
    const handleShiftTab = () => {
      focusFilters.focusFilterSidebar()
    }

    return { canLoadMore, onLoadMore, handleShiftTab, results }
  },
  head: {},
})
</script>
