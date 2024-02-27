<template>
  <VSearchResults
    :results="results"
    kind="search"
    :search-term="searchTerm"
    @load-more="handleLoadMore"
  />
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { AudioResults } from "~/types/result"

import VSearchResults from "~/components/VSearchResultsGrid/VSearchResults.vue"

export default defineComponent({
  name: "AudioSearch",
  components: {
    VSearchResults,
  },
  props: {
    results: {
      type: Object as PropType<AudioResults>,
      required: true,
    },
    searchTerm: {
      type: String,
      required: true,
    },
    handleLoadMore: {
      type: Function as PropType<() => void>,
      required: true,
    },
  },
})
</script>
