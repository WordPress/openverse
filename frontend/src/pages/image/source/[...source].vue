<template>
  <VCollectionPage media-type="image" />
</template>

<script lang="ts">
import {
  defineNuxtComponent,
  definePageMeta,
  useAsyncData,
  useRoute,
} from "#imports"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { parseCollectionPath } from "~/utils/parse-collection-path"
import { IMAGE } from "~/constants/media"
import { collectionMiddleware } from "~/middleware/collection"

import VCollectionPage from "~/components/VCollectionPage.vue"

export default defineNuxtComponent({
  name: "VImageSourcePage",
  components: { VCollectionPage },
  setup() {
    definePageMeta({
      layout: "content-layout",
      middleware: collectionMiddleware,
    })
    const route = useRoute()
    const collectionParams = parseCollectionPath(route.params.source)
    if (!collectionParams) {
      throw new Error("Invalid collection path")
    }
    useSearchStore().setCollectionState(collectionParams, IMAGE)
    const mediaStore = useMediaStore()

    useAsyncData("image-source", async () => {
      await mediaStore.fetchMedia()
    })
    return {}
  },
})
</script>
