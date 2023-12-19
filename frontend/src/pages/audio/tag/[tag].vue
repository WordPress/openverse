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
import { AUDIO } from "~/constants/media"
import type { TagCollection } from "~/types/search"
import { collectionMiddleware } from "~/middleware/collection"

import VCollectionPage from "~/components/VCollectionPage.vue"

export default defineNuxtComponent({
  name: "VAudioTagPage",
  components: { VCollectionPage },
  setup() {
    definePageMeta({
      layout: "content-layout",
      middleware: collectionMiddleware,
    })
    const route = useRoute()
    const collectionParams: TagCollection = {
      tag: route.params.tag,
      collection: "tag",
    }
    useSearchStore().setCollectionState(collectionParams, AUDIO)

    const mediaStore = useMediaStore()

    useAsyncData("audio-tag", async () => {
      await mediaStore.fetchMedia()
    })
    return {}
  },
})
</script>
