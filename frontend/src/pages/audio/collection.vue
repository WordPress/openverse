<script setup lang="ts">
import { definePageMeta, useAsyncData, useHead } from "#imports"

import { collectionMiddleware } from "~/middleware/collection"

import { skipToContentTargetId } from "~/constants/window"

import { useCollection } from "~/composables/use-collection"
import { usePageRobotsRule } from "~/composables/use-page-robots-rule"
import { AUDIO } from "~/constants/media"

import { CollectionParams } from "~/types/search"

import VCollectionResults from "~/components/VSearchResultsGrid/VCollectionResults.vue"

defineOptions({
  name: "AudioCollection",
})

definePageMeta({
  layout: "content-layout",
  middleware: collectionMiddleware,
})

const {
  collectionParams,
  isFetching,
  media,
  creatorUrl,
  collectionLabel,
  fetchMedia,
  loadMore,
  pageTitle,
} = useCollection({ mediaType: AUDIO })

// Collection params are not nullable in the collections route, this is enforced by the middleware
// Question: should this non-nullability be filtered in the type and enforced in runtime by `useCollection`?
usePageRobotsRule(
  `${(collectionParams.value as NonNullable<CollectionParams>).collection}-collection`
)

useHead({
  meta: [{ hid: "og:title", property: "og:title", content: pageTitle.value }],
  title: pageTitle.value,
})

/**
 * Media is not empty when we navigate back to this page, so we don't need to fetch
 * it again to make sure that all the previously fetched media is displayed.
 */
await useAsyncData(
  "audio-collection",
  async () => (media.value.length ? media.value : await fetchMedia()),
  { lazy: true, server: false }
)
</script>

<template>
  <div
    :id="skipToContentTargetId"
    tabindex="-1"
    class="p-6 pt-0 lg:p-10 lg:pt-2"
  >
    <VCollectionResults
      v-if="collectionParams"
      search-term=""
      :is-fetching="isFetching"
      :results="{ type: 'audio', items: media }"
      :collection-label="collectionLabel"
      :collection-params="collectionParams"
      :creator-url="creatorUrl"
      @load-more="loadMore"
    />
  </div>
</template>
