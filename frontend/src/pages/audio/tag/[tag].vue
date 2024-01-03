<template>
  <VCollectionPage media-type="audio" />
</template>

<script lang="ts">
import { defineNuxtComponent, definePageMeta, useRoute } from "#imports"

import { useFetch } from "@nuxtjs/composition-api"

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
    const tag = Array.isArray(route.params.tag)
      ? route.params.tag[0]
      : route.params.tag
    const collectionParams: TagCollection = {
      tag,
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
