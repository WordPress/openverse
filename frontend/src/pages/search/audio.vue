<script setup lang="ts">
import type { AudioResults } from "~/types/result"

import VSearchResults from "~/components/VSearchResultsGrid/VSearchResults.vue"

defineOptions({
  name: "AudioSearch",
})

defineProps<{
  results: AudioResults
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
