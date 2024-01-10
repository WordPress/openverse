<template>
  <VAllResultsGrid :results="results" :search-term="searchTerm" />
</template>

<script lang="ts">
import { defineNuxtComponent } from "#imports"

import type { AudioDetail, ImageDetail } from "~/types/media"

import VAllResultsGrid from "~/components/VSearchResultsGrid/VAllResultsGrid.vue"

import type { PropType } from "vue"

export default defineNuxtComponent({
  name: "SearchIndex",
  components: { VAllResultsGrid },
  props: {
    results: {
      type: Array as PropType<(ImageDetail | AudioDetail)[]>,
      default: () => [],
    },
    searchTerm: {
      type: String,
      required: true,
    },
  },
})
</script>
