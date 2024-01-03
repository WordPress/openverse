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
import { IMAGE } from "~/constants/media"
import { collectionMiddleware } from "~/middleware/collection"
import type { TagCollection } from "~/types/search"

import VCollectionPage from "~/components/VCollectionPage.vue"

export default defineNuxtComponent({
  name: "VImageTagPage",
  components: { VCollectionPage },
  setup() {
    definePageMeta({
      layout: "content-layout",
      middleware: collectionMiddleware,
    })
    const route = useRoute()
    const tag = Array.isArray(route.params.tag)
      ? route.params.tag[0]
      : route.params.tag
    const collectionParams: TagCollection = {
      tag,
      collection: "tag",
    }
    useSearchStore().setCollectionState(collectionParams, IMAGE)

    const mediaStore = useMediaStore()

    useAsyncData(
      "image-tag",
      async () => {
        await mediaStore.fetchMedia()
      },
      { server: false }
    )
    return {}
  },
})
</script>
