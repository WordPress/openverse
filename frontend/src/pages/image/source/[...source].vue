<template>
  <VCollectionPage media-type="image" />
</template>

<script lang="ts">
import { defineNuxtComponent, definePageMeta, useAsyncData } from "#imports"

import { useMediaStore } from "~/stores/media"
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
