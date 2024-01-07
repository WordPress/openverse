<template>
  <VImageGrid
    :results="results"
    :fetch-state="fetchState"
    kind="search"
    :image-grid-label="$t('browsePage.aria.results', { query: searchTerm })"
  />
</template>

<script lang="ts">
import { defineNuxtComponent } from "#imports"

import { computed } from "vue"

import { useMediaStore } from "~/stores/media"

import VImageGrid from "~/components/VSearchResultsGrid/VImageGrid.vue"

export default defineNuxtComponent({
  name: "ImageSearch",
  components: { VImageGrid },
  props: {
    searchTerm: {
      type: String,
      required: true,
    },
  },
  setup() {
    const mediaStore = useMediaStore()
    const results = computed(() => mediaStore.resultItems["image"])
    const fetchState = computed(() => mediaStore.fetchState)

    return {
      results,
      fetchState,
    }
  },
})
</script>
