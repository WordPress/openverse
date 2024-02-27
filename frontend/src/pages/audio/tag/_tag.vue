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

import { useMediaStore } from "~/stores/media"
import { useCollectionResults } from "~/composables/use-collection-results"
import { AUDIO } from "~/constants/media"
import { collectionMiddleware } from "~/middleware/collection"

import { useSearchStore } from "~/stores/search"

import VCollectionPage from "~/components/VCollectionPage.vue"

export default defineComponent({
  name: "VAudioTagPage",
  components: { VCollectionPage },
  layout: "content-layout",
  middleware: collectionMiddleware,
  setup() {
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()

    const collectionParams = computed(() => searchStore.collectionParams)

    const { results, fetchMedia, handleLoadMore } =
      useCollectionResults<typeof AUDIO>(AUDIO)

    useFetch(async () => {
      if (mediaStore.resultItems.audio.length === 0) {
        await fetchMedia({ shouldPersistMedia: false })
      }
    })
    return {
      collectionParams,
      results,
      handleLoadMore,
    }
  },
})
</script>
