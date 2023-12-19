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

import { PropType } from "vue"

import type { ImageDetail } from "~/types/media"
import type { FetchState } from "~/types/fetch-state"

import VImageGrid from "~/components/VSearchResultsGrid/VImageGrid.vue"

export default defineNuxtComponent({
  name: "ImageSearch",
  components: { VImageGrid },
  props: {
    results: {
      type: Array as PropType<ImageDetail[]>,
      required: true,
    },
    fetchState: {
      type: Object as PropType<FetchState>,
      required: true,
    },
    searchTerm: {
      type: String,
      required: true,
    },
  },
})
</script>
