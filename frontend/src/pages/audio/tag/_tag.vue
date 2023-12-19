<template>
  <VCollectionPage media-type="audio" />
</template>

<script lang="ts">
import { defineNuxtComponent } from "#imports"

import { useFetch, useRoute } from "@nuxtjs/composition-api"

import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { AUDIO } from "~/constants/media"
import type { TagCollection } from "~/types/search"
import { collectionMiddleware } from "~/middleware/collection"

import VCollectionPage from "~/components/VCollectionPage.vue"

export default defineNuxtComponent({
  name: "VAudioTagPage",
  components: { VCollectionPage },
  layout: "content-layout",
  middleware: collectionMiddleware,
  setup() {
    const route = useRoute()
    const collectionParams: TagCollection = {
      tag: route.value.params.tag,
      collection: "tag",
    }
    useSearchStore().setCollectionState(collectionParams, AUDIO)

    const mediaStore = useMediaStore()

    useFetch(async () => {
      await mediaStore.fetchMedia()
    })
    return {}
  },
})
</script>
