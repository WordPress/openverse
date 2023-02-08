<template>
  <VImageGrid
    :images="results"
    :is-single-page="false"
    :fetch-state="fetchState"
    @shift-tab="handleShiftTab"
  />
</template>

<script lang="ts">
import { computed, defineComponent, useMeta } from "@nuxtjs/composition-api"

import { propTypes } from "~/pages/search/search-page.types"
import { useFocusFilters } from "~/composables/use-focus-filters"

import VImageGrid from "~/components/VImageGrid/VImageGrid.vue"

export default defineComponent({
  name: "ImageSearch",
  components: { VImageGrid },
  props: propTypes,
  setup(props) {
    useMeta({
      title: `${props.searchTerm} | Openverse`,
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
