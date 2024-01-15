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
      :results="{ type: 'image', items: media }"
      :collection-label="collectionLabel"
      :collection-params="collectionParams"
      @load-more="loadMore"
    />
  </div>
</template>

<script setup lang="ts">
import {
  definePageMeta,
  useAsyncData,
  useHead,
  useI18n,
  useRoute,
} from "#imports"

import { computed, ref, watch } from "vue"

import { collectionMiddleware } from "~/middleware/collection"
import { useMediaStore } from "~/stores/media"
import { useSearchStore } from "~/stores/search"
import { useCollectionMeta } from "~/composables/use-collection-meta"
import { skipToContentTargetId } from "~/constants/window"
import type { ImageDetail } from "~/types/media"

import VCollectionResults from "~/components/VSearchResultsGrid/VCollectionResults.vue"

definePageMeta({
  layout: "content-layout",
  middleware: collectionMiddleware,
})

const mediaStore = useMediaStore()
const searchStore = useSearchStore()

const collectionParams = computed(() => searchStore.collectionParams)
const isFetching = computed(() => mediaStore.fetchState.isFetching)

const media = ref<ImageDetail[]>(mediaStore.resultItems.image)
const creatorUrl = ref<string>()

const i18n = useI18n({ useScope: "global" })

const collectionLabel = computed(() => {
  if (!collectionParams.value) {
    return ""
  }
  const { collection, ...params } = collectionParams.value
  return i18n.t(`collection.ariaLabel.${collection}.image`, { ...params })
})

const fetchMedia = async (
  { shouldPersistMedia }: { shouldPersistMedia: boolean } = {
    shouldPersistMedia: false,
  }
) => {
  media.value = (await mediaStore.fetchMedia({
    shouldPersistMedia,
  })) as ImageDetail[]
  creatorUrl.value =
    media.value.length > 0 ? media.value[0].creator_url : undefined
  return media.value
}
const loadMore = () => {
  fetchMedia({ shouldPersistMedia: true })
}

const { pageTitle } = useCollectionMeta({
  collectionParams,
  mediaType: "image",
  i18n,
})

useHead(() => ({
  meta: [
    { hid: "robots", name: "robots", content: "all" },
    { hid: "og:title", property: "og:title", content: pageTitle.value },
  ],
  title: pageTitle.value,
}))

// `useAsyncData` is not triggered when the query changes, e.g. when the user navigates from
// a creator collection page to a source collection page.
const route = useRoute()
const routeQuery = computed(() => route.query)
watch(routeQuery, async () => {
  await fetchMedia()
})

/**
 * Media is not empty when we navigate back to this page, so we don't need
 * to fetch it again to make sure that all the previously fetched media is displayed.
 */
await useAsyncData(
  "image-collection",
  async () => (media.value.length ? media.value : await fetchMedia()),
  { lazy: true, server: false }
)
</script>
