<script setup lang="ts">
import { useRoute, useI18n } from "#imports"
import { computed, watch } from "vue"

import type { SupportedMediaType } from "#shared/constants/media"
import { firstParam } from "#shared/utils/query-utils"
import type { AudioResults, ImageResults } from "#shared/types/result"
import { useRelatedMediaStore } from "~/stores/media/related-media"

import VMediaCollection from "~/components/VSearchResultsGrid/VMediaCollection.vue"

const props = defineProps<{
  mediaType: SupportedMediaType
  relatedTo: string
}>()

const relatedMediaStore = useRelatedMediaStore()

const route = useRoute()

const results = computed(() => {
  const media = relatedMediaStore.media ?? []
  return { type: props.mediaType, items: media } as ImageResults | AudioResults
})
watch(
  route,
  async (newRoute) => {
    const mediaId = firstParam(newRoute?.params.id)
    if (mediaId && mediaId !== relatedMediaStore.mainMediaId) {
      await relatedMediaStore.fetchMedia(props.mediaType, mediaId)
    }
  },
  { immediate: true }
)

const isFetching = computed(() => relatedMediaStore.fetchState.isFetching)
const showRelated = computed(
  () => results.value.items.length > 0 || isFetching.value
)

const searchTerm = computed(() => {
  return firstParam(route?.query.q) ?? ""
})

const { t } = useI18n({ useScope: "global" })

const collectionLabel = computed(() => {
  const key =
    props.mediaType === "audio"
      ? "audioDetails.relatedAudios"
      : "imageDetails.relatedImages"
  return t(key)
})
</script>

<template>
  <VMediaCollection
    v-if="showRelated"
    :results="results"
    :is-fetching="isFetching"
    :collection-label="collectionLabel"
    kind="related"
    :related-to="relatedTo"
    :search-term="searchTerm"
    :aria-label="collectionLabel"
  >
    <template #header>
      <h2 id="related-heading" class="heading-6 md:heading-5 mb-6">
        {{ collectionLabel }}
      </h2>
    </template>
  </VMediaCollection>
</template>
