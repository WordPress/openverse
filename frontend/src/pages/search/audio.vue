<template>
  <VMediaCollection
    :results="results"
    :metadata="{ searchTerm, kind: 'search' }"
    :collection-label="
      $t('browsePage.aria.results', { query: searchTerm }).toString()
    "
    @load-more="handleLoadMore"
  />
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { AudioResults } from "~/types/result"

import VMediaCollection from "~/components/VSearchResultsGrid/VMediaCollection.vue"

export default defineComponent({
  name: "AudioSearch",
  components: {
    VMediaCollection,
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
