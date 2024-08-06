<template>
  <VMediaCollection
    :results="results"
    :is-fetching="isFetching"
    :search-term="searchTerm"
    :collection-label="collectionLabel"
    kind="collection"
  >
    <template #header>
      <VCollectionHeader
        v-if="isSupportedMediaType(results.type)"
        class="mb-2 md:mb-3"
        :media-type="results.type"
        :collection-params="collectionParams"
        :creator-url="creatorUrl"
      />
    </template>

    <template #footer>
      <footer class="mb-6 mt-4 lg:mb-10">
        <VLoadMore
          :search-type="results.type"
          kind="collection"
          :search-term="searchTerm"
          :is-fetching="isFetching"
          class="mb-4"
          @load-more="$emit('load-more')"
        />
      </footer>
    </template>
  </VMediaCollection>
</template>

<script lang="ts">
import { defineComponent, type PropType } from "vue"

import { isSupportedMediaType } from "~/constants/media"

import type { CollectionParams } from "~/types/search"
import type { AudioResults, ImageResults } from "~/types/result"

import { defineEvent } from "~/types/emits"

import VCollectionHeader from "~/components/VCollectionHeader/VCollectionHeader.vue"
import VMediaCollection from "~/components/VSearchResultsGrid/VMediaCollection.vue"
import VLoadMore from "~/components/VLoadMore.vue"

export default defineComponent({
  name: "VCollectionResults",
  components: { VLoadMore, VMediaCollection, VCollectionHeader },
  props: {
    collectionParams: {
      type: Object as PropType<CollectionParams>,
      required: true,
    },
    collectionLabel: {
      type: String,
      required: true,
    },
    results: {
      type: Object as PropType<ImageResults | AudioResults>,
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
    creatorUrl: {
      type: String,
    },
  },
  emits: {
    "load-more": defineEvent(),
  },
  methods: { isSupportedMediaType },
})
</script>
