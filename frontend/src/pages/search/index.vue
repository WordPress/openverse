<template>
  <VSearchResults
    :results="results"
    :is-fetching="isFetching"
    :search-term="searchTerm"
    kind="search"
    @load-more="handleLoadMore"
  />
</template>

<script lang="ts">
import { defineComponent, type PropType } from "vue"

import type { AllMediaResults } from "~/types/result"

import VSearchResults from "~/components/VSearchResultsGrid/VSearchResults.vue"

export default defineComponent({
  name: "SearchIndex",
  components: { VSearchResults },
  props: {
    results: {
      type: Object as PropType<AllMediaResults>,
      required: true,
    },
    isFetching: {
      type: Boolean,
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
