<script setup lang="ts">
import { isSupportedMediaType } from "~/constants/media"

import type { CollectionParams } from "~/types/search"
import type { AudioResults, ImageResults } from "~/types/result"

import VCollectionHeader from "~/components/VCollectionHeader/VCollectionHeader.vue"
import VMediaCollection from "~/components/VSearchResultsGrid/VMediaCollection.vue"
import VLoadMore from "~/components/VLoadMore.vue"

defineProps<{
  collectionParams: CollectionParams
  collectionLabel: string
  results: ImageResults | AudioResults
  isFetching: boolean
  searchTerm: string
  creatorUrl?: string
}>()

defineEmits<{ "load-more": [] }>()
</script>

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
