<template>
  <VSearchResults
    :results="results"
    kind="search"
    :search-term="searchTerm"
    @load-more="handleLoadMore"
  />
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { ImageResults } from "~/types/result"

import VSearchResults from "~/components/VSearchResultsGrid/VSearchResults.vue"

export default defineComponent({
  name: "ImageSearch",
  components: { VSearchResults },
  props: {
    results: {
      type: Object as PropType<ImageResults>,
      required: true,
    },
    searchTerm: {
      type: String,
      required: true,
    },
    handleLoadMore: {
      type: Function as PropType<() => void>,
      required: true,
    },
  },
})
</script>
