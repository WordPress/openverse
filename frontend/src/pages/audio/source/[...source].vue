<template>
  <VCollectionPage media-type="audio" />
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
import { AUDIO } from "~/constants/media"
import { collectionMiddleware } from "~/middleware/collection"

import VCollectionPage from "~/components/VCollectionPage.vue"

export default defineNuxtComponent({
  name: "VAudioSourcePage",
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
    useSearchStore().setCollectionState(collectionParams, AUDIO)
    const mediaStore = useMediaStore()

    useAsyncData(
      "image-source",
      async () => {
        await mediaStore.fetchMedia()
      },
      { server: false }
    )

    return {}
  },
})
</script>
