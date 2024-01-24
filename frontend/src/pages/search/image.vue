<template>
  <VImageGrid
    :results="results"
    kind="search"
    :image-grid-label="$t('browsePage.aria.results', { query: searchTerm })"
  />
</template>

<script setup lang="ts">
import type { ImageDetail } from "~/types/media"

import VImageGrid from "~/components/VSearchResultsGrid/VImageGrid.vue"

defineProps<{
  searchTerm: string
  results: ImageDetail[]
}>()
</script>
