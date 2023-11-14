<template>
  <div class="px-6 lg:px-10">
    <VCollectionHeader
      v-if="collectionParams"
      :collection-params="collectionParams"
      :creator-url="creatorUrl"
      :media-type="mediaType"
      class="mb-6"
    />
    <VAudioCollection
      v-if="results.type === 'audio'"
      collection-label="audio collection"
      :fetch-state="fetchState"
      kind="collection"
      :results="results.items"
    />
    <VImageGrid
      v-if="results.type === 'image'"
      image-grid-label="image collection"
      :fetch-state="fetchState"
      kind="collection"
      :results="results.items"
    />
  </div>
</template>
<script lang="ts">
import { computed, PropType } from "vue"

import { CollectionParams } from "~/types/search"
import { SupportedMediaType } from "~/constants/media"

import { useMediaStore } from "~/stores/media"

import { Results } from "~/types/result"

import VCollectionHeader from "~/components/VCollectionHeader/VCollectionHeader.vue"
import VAudioCollection from "~/components/VSearchResultsGrid/VAudioCollection.vue"
import VImageGrid from "~/components/VSearchResultsGrid/VImageGrid.vue"

export default {
  name: "VCollectionPage",
  components: { VAudioCollection, VImageGrid, VCollectionHeader },
  props: {
    results: {
      type: Object as PropType<Results>,
      required: true,
    },
    collectionParams: {
      type: Object as PropType<CollectionParams>,
      required: true,
    },
    mediaType: {
      type: String as PropType<SupportedMediaType>,
      required: true,
    },
    creatorUrl: {
      type: String,
    },
  },
  setup() {
    const mediaStore = useMediaStore()

    const fetchState = computed(() => mediaStore.fetchState)

    return {
      fetchState,
    }
  },
}
</script>
