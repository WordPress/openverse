<script setup lang="ts">
import type { ImageResults } from "~/types/result"

import VSearchResults from "~/components/VSearchResultsGrid/VSearchResults.vue"

defineOptions({
  name: "ImageSearch",
})

defineProps<{
  results: ImageResults
  isFetching: boolean
  searchTerm: string
  handleLoadMore: () => void
}>()
</script>

<template>
  <VSearchResults
    :results="results"
    :is-fetching="isFetching"
    :search-term="searchTerm"
    kind="search"
    @load-more="handleLoadMore"
  />
</template>
