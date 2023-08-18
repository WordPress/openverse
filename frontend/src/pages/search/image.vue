<template>
  <VImageGrid
    :images="results"
    :is-single-page="false"
    :fetch-state="fetchState"
    :image-grid-label="
      $t('browsePage.aria.results', { query: searchTerm }).toString()
    "
  />
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { ImageDetail } from "~/types/media"
import type { FetchingError, FetchState } from "~/types/fetch-state"

import VImageGrid from "~/components/VSearchResultsGrid/VImageGrid.vue"

export default defineComponent({
  name: "ImageSearch",
  components: { VImageGrid },
  props: {
    results: {
      type: Array as PropType<ImageDetail[]>,
      required: true,
    },
    fetchState: {
      type: Object as PropType<FetchState<FetchingError>>,
      required: true,
    },
    searchTerm: {
      type: String,
      required: true,
    },
  },
})
</script>
