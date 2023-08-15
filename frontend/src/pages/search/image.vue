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
import type { FetchState } from "~/types/fetch-state"

import VImageGrid from "~/components/VSearchResultsGrid/VImageGrid.vue"

import type { NuxtError } from "@nuxt/types"

export default defineComponent({
  name: "ImageSearch",
  components: { VImageGrid },
  props: {
    results: {
      type: Array as PropType<ImageDetail[]>,
      required: true,
    },
    fetchState: {
      type: Object as PropType<FetchState<NuxtError> | FetchState>,
      required: true,
    },
    searchTerm: {
      type: String,
      required: true,
    },
  },
})
</script>
