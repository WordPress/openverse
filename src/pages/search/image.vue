<template>
  <VImageGrid
    :images="results"
    :is-single-page="false"
    :fetch-state="fetchState"
    @shift-tab="handleShiftTab"
  />
</template>

<script lang="ts">
import { computed, defineComponent, useMeta } from '@nuxtjs/composition-api'

import { propTypes } from '~/pages/search/search-page.types'
import { useFocusFilters } from '~/composables/use-focus-filters'
import { useFeatureFlagStore } from '~/stores/feature-flag'

import VImageGrid from '~/components/VImageGrid/VImageGrid.vue'

export default defineComponent({
  name: 'ImageSearch',
  components: { VImageGrid },
  props: propTypes,
  setup(props) {
    const featureFlagStore = useFeatureFlagStore()

    useMeta({
      title: `${props.searchTerm} | Openverse`,
      meta: featureFlagStore.isOn('new_header')
        ? [{ hid: 'robots', name: 'robots', content: 'all' }]
        : undefined,
    })

    const results = computed(() => props.resultItems.image)

    const focusFilters = useFocusFilters()
    const handleShiftTab = () => {
      focusFilters.focusFilterSidebar()
    }

    return { handleShiftTab, results }
  },
  head: {},
})
</script>
