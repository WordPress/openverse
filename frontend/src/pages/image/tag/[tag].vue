<template>
  <VCollectionPage
    :is-fetching="pending"
    media-type="image"
    @load-more="handleLoadMore"
  />
</template>

<script lang="ts">
import { defineNuxtComponent, definePageMeta } from "#imports"

import { collectionMiddleware } from "~/middleware/collection"

import { useCollectionFetching } from "~/composables/use-collection-fetching"

import VCollectionPage from "~/components/VCollectionPage.vue"

export default defineNuxtComponent({
  name: "VImageTagPage",
  components: { VCollectionPage },
  async setup() {
    definePageMeta({
      layout: "content-layout",
      middleware: collectionMiddleware,
    })

    const { pending, handleLoadMore } = await useCollectionFetching({
      collectionId: "image-tag ",
    })

    return {
      handleLoadMore,
      pending,
    }
  },
})
</script>
