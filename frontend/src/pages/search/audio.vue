<template>
  <VSearchResults
    :results="results"
    :is-fetching="isFetching"
    :search-term="searchTerm"
    kind="search"
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
    isFetching: {
      type: Boolean,
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
