<template>
  <div class="p-6 lg:p-10">
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
import { computed, defineComponent, PropType } from "vue"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import type { SupportedMediaType } from "~/constants/media"

import { Results } from "~/types/result"

import VCollectionHeader from "~/components/VCollectionHeader/VCollectionHeader.vue"
import VAudioCollection from "~/components/VSearchResultsGrid/VAudioCollection.vue"
import VImageGrid from "~/components/VSearchResultsGrid/VImageGrid.vue"

export default defineComponent({
  name: "VCollectionPage",
  components: { VAudioCollection, VImageGrid, VCollectionHeader },
  props: {
    mediaType: {
      type: String as PropType<SupportedMediaType>,
      required: true,
    },
  },
  setup(props) {
    const mediaStore = useMediaStore()

    const fetchState = computed(() => mediaStore.fetchState)
    const results = computed<Results>(() => {
      return {
        type: props.mediaType,
        items: mediaStore.resultItems[props.mediaType],
      } as Results
    })

    const creatorUrl = computed(() => {
      const media = results.value.items
      return media.length > 0 ? media[0].creator_url : undefined
    })

    const searchStore = useSearchStore()
    const collectionParams = computed(() => searchStore.collectionParams)

    return {
      fetchState,
      results,
      creatorUrl,
      collectionParams,
    }
  },
})
</script>
