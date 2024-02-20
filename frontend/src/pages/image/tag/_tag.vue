<template>
  <VCollectionPage media-type="image" />
</template>

<script lang="ts">
import { defineComponent, useFetch } from "@nuxtjs/composition-api"

import { useMediaStore } from "~/stores/media"
import { collectionMiddleware } from "~/middleware/collection"

import VCollectionPage from "~/components/VCollectionPage.vue"

export default defineComponent({
  name: "VImageTagPage",
  components: { VCollectionPage },
  layout: "content-layout",
  middleware: collectionMiddleware,
  setup() {
    const mediaStore = useMediaStore()

    useFetch(async () => {
      await mediaStore.fetchMedia()
    })
    return {}
  },
})
</script>
