<template>
  <VCollectionPage media-type="image" />
</template>

<script lang="ts">
import { defineNuxtComponent, useRoute } from "#imports"

import { useFetch } from "@nuxtjs/composition-api"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { IMAGE } from "~/constants/media"
import { collectionMiddleware } from "~/middleware/collection"
import type { TagCollection } from "~/types/search"

import VCollectionPage from "~/components/VCollectionPage.vue"

export default defineNuxtComponent({
  name: "VImageTagPage",
  components: { VCollectionPage },
  layout: "content-layout",
  middleware: collectionMiddleware,
  setup() {
    const route = useRoute()
    const collectionParams: TagCollection = {
      tag: route.params.tag,
      collection: "tag",
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
