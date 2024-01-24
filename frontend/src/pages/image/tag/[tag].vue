<template>
  <VCollectionPage
    :is-fetching="pending"
    media-type="image"
    @load-more="handleLoadMore"
  />
</template>

<script setup lang="ts">
import { definePageMeta } from "#imports"

import { collectionMiddleware } from "~/middleware/collection"

import { useCollectionFetching } from "~/composables/use-collection-fetching"

import VCollectionPage from "~/components/VCollectionPage.vue"

definePageMeta({
  layout: "content-layout",
  middleware: collectionMiddleware,
})

const { pending, handleLoadMore } = await useCollectionFetching({
  collectionId: "image-tag ",
})
</script>
