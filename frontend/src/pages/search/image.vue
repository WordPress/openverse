<template>
  <VImageGrid
    :results="results"
    kind="search"
    :image-grid-label="t('browsePage.aria.results', { query: searchTerm })"
  />
</template>

<script setup lang="ts">
import { useNuxtApp } from "#imports"

import type { ImageDetail } from "~/types/media"

import VImageGrid from "~/components/VSearchResultsGrid/VImageGrid.vue"

defineProps<{
  searchTerm: string
  results: ImageDetail[]
}>()

const {
  $i18n: { t },
} = useNuxtApp()
</script>
