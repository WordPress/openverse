<template>
  <VCollectionPage media-type="image" />
</template>

<script lang="ts">
import { defineNuxtComponent, useRoute } from "#imports"

import { useFetch } from "@nuxtjs/composition-api"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { parseCollectionPath } from "~/utils/parse-collection-path"
import { IMAGE } from "~/constants/media"
import { collectionMiddleware } from "~/middleware/collection"

import VCollectionPage from "~/components/VCollectionPage.vue"

export default defineNuxtComponent({
  name: "VImageSourcePage",
  components: { VCollectionPage },
  layout: "content-layout",
  middleware: collectionMiddleware,
  setup() {
    const route = useRoute()
    const collectionParams = parseCollectionPath(route.params.pathMatch)
    if (!collectionParams) {
      throw new Error("Invalid collection path")
    }
    useSearchStore().setCollectionState(collectionParams, IMAGE)
    const mediaStore = useMediaStore()

    useFetch(async () => {
      await mediaStore.fetchMedia()
    })
    return {}
  },
})
</script>
