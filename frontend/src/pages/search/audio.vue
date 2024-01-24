<template>
  <VAudioCollection
    :results="results"
    kind="search"
    :collection-label="collectionLabel"
  />
</template>

<script setup lang="ts">
import { useI18n } from "#imports"

import { computed } from "vue"

import { useSearchStore } from "~/stores/search"

import type { AudioDetail } from "~/types/media"

import VAudioCollection from "~/components/VSearchResultsGrid/VAudioCollection.vue"

defineProps<{
  searchTerm: string
  results: AudioDetail[]
}>()

const i18n = useI18n({ useScope: "global" })
const searchStore = useSearchStore()

const collectionLabel = computed(() => {
  const query = searchStore.searchTerm

  return i18n.t("browsePage.aria.results", { query })
})
</script>
