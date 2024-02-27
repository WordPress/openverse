<template>
  <section>
    <VMediaCollection
      :results="results"
      :collection-label="collectionLabel"
      kind="related"
      :related-to="relatedTo"
      :search-term="searchTerm"
    >
      <template #header>
        <h2 class="heading-6 md:heading-5 mb-6">
          {{ collectionLabel }}
        </h2>
      </template>
    </VMediaCollection>
  </section>
</template>

<script lang="ts">
import { defineComponent, type PropType } from "vue"

import type { AudioResults, ImageResults } from "~/types/result"

import VMediaCollection from "~/components/VSearchResultsGrid/VMediaCollection.vue"

export default defineComponent({
  name: "VRelatedResults",
  components: { VMediaCollection },
  props: {
    results: {
      type: Object as PropType<ImageResults | AudioResults>,
      required: true,
    },
    collectionLabel: {
      type: String as PropType<string>,
      required: true,
    },
    searchTerm: {
      type: String as PropType<string>,
      required: true,
    },
    relatedTo: {
      type: String as PropType<string>,
      required: true,
    },
  },
})
</script>
