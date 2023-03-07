<template>
  <VImageGrid
    :images="results"
    :is-single-page="false"
    :fetch-state="fetchState"
  />
</template>

<script lang="ts">
import { computed, defineComponent } from "vue"

import { propTypes } from "~/pages/search/search-page.types"

import VImageGrid from "~/components/VSearchResultsGrid/VImageGrid.vue"

export default defineComponent({
  name: "ImageSearch",
  components: { VImageGrid },
  props: propTypes,
  setup(props) {
    const results = computed(() => props.resultItems.image)

    return { results }
  },
})
</script>
