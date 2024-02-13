<template>
  <VCollectionPage
    v-if="collectionParams"
    :results="results"
    :collection-params="collectionParams"
    @load-more="handleLoadMore"
  />
</template>

<script lang="ts">
import { defineComponent, useFetch } from "@nuxtjs/composition-api"

import { computed } from "vue"

import { useCollectionResults } from "~/composables/use-collection-results"
import { useMediaStore } from "~/stores/media"
import { collectionMiddleware } from "~/middleware/collection"

import { IMAGE } from "~/constants/media"
import { useSearchStore } from "~/stores/search"

import VCollectionPage from "~/components/VCollectionPage.vue"

export default defineComponent({
  name: "VImageSourcePage",
  components: { VCollectionPage },
  layout: "content-layout",
  middleware: collectionMiddleware,
  setup() {
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()

    const collectionParams = computed(() => searchStore.collectionParams)

    const { results, fetchMedia, handleLoadMore, creatorUrl } =
      useCollectionResults<typeof IMAGE>(IMAGE)

    useFetch(async () => {
      if (mediaStore.resultItems[IMAGE].length === 0) {
        await fetchMedia({ shouldPersistMedia: false })
      }
    })
    return {
      results,
      creatorUrl,
      collectionParams,
      handleLoadMore,
    }
  },
})
</script>
