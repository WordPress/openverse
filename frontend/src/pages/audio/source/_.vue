<template>
  <VCollectionPage
    v-if="collectionParams"
    :collection-params="collectionParams"
    :results="results"
    :creator-url="creatorUrl"
    @load-more="handleLoadMore"
  />
</template>

<script lang="ts">
import { defineComponent, useFetch } from "@nuxtjs/composition-api"

import { computed } from "vue"

import { useMediaStore } from "~/stores/media"
import { AUDIO } from "~/constants/media"
import { collectionMiddleware } from "~/middleware/collection"

import { useCollectionResults } from "~/composables/use-collection-results"
import { useSearchStore } from "~/stores/search"

import VCollectionPage from "~/components/VCollectionPage.vue"

export default defineComponent({
  name: "VAudioSourcePage",
  components: { VCollectionPage },
  layout: "content-layout",
  middleware: collectionMiddleware,
  setup() {
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()

    const collectionParams = computed(() => searchStore.collectionParams)

    const { results, fetchMedia, handleLoadMore, creatorUrl } =
      useCollectionResults<typeof AUDIO>(AUDIO)

    useFetch(async () => {
      if (mediaStore.resultItems.image.length === 0) {
        await fetchMedia({ shouldPersistMedia: false })
      }
    })

    return {
      results,
      collectionParams,
      handleLoadMore,
      creatorUrl,
    }
  },
})
</script>
