<template>
  <VAllResultsGrid :results="results" :search-term="searchTerm" />
</template>

<script setup lang="ts">
import type { AudioDetail, ImageDetail } from "~/types/media"

import VAllResultsGrid from "~/components/VSearchResultsGrid/VAllResultsGrid.vue"

defineProps<{
  searchTerm: string
  results: (AudioDetail | ImageDetail)[]
}>()
</script>
