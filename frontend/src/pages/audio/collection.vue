<template>
  <div class="p-6 pt-0 lg:p-10 lg:pt-2">
    <VCollectionResults
      v-if="collectionParams"
      search-term=""
      :is-fetching="isFetching"
      :results="results"
      :collection-label="collectionLabel"
      :collection-params="collectionParams"
      @load-more="handleLoadMore"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, useFetch, useMeta } from "@nuxtjs/composition-api"
import { computed } from "vue"

import { collectionMiddleware } from "~/middleware/collection"
import { useSearchStore } from "~/stores/search"
import { useCollection } from "~/composables/use-collection"
import { AUDIO } from "~/constants/media"

import VCollectionResults from "~/components/VSearchResultsGrid/VCollectionResults.vue"

export default defineComponent({
  name: "VAudioCollectionPage",
  components: { VCollectionResults },
  layout: "content-layout",
  middleware: collectionMiddleware,
  setup() {
    const searchStore = useSearchStore()

    const collectionParams = computed(() => searchStore.collectionParams)

    const {
      results,
      creatorUrl,
      fetchMedia,
      handleLoadMore,
      collectionLabel,
      isFetching,
    } = useCollection({
      mediaType: AUDIO,
    })

    useFetch(async () => {
      await fetchMedia()
    })

    useMeta({
      meta: [{ hid: "robots", name: "robots", content: "all" }],
    })

    return {
      results,
      collectionParams,
      isFetching,
      creatorUrl,
      collectionLabel,
      handleLoadMore,
    }
  },
  head: {},
})
</script>
