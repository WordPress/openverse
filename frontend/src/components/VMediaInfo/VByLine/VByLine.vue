<script setup lang="ts">
import { computed } from "vue"

import { useSearchStore } from "~/stores/search"
import type { AudioDetail, ImageDetail } from "~/types/media"

import VSourceCreatorButton from "~/components/VMediaInfo/VByLine/VSourceCreatorButton.vue"
import VScrollableLine from "~/components/VScrollableLine.vue"

/**
 * A link to a collection page, either a source or a creator.
 */
const props = defineProps<{
  media: AudioDetail | ImageDetail
}>()
const searchStore = useSearchStore()

const creator = computed(() => {
  if (props.media.creator && props.media.creator !== "unidentified") {
    const href = searchStore.getCollectionPath({
      type: props.media.frontendMediaType,
      collectionParams: {
        collection: "creator",
        source: props.media.source,
        creator: props.media.creator,
      },
    })
    return { name: props.media.creator, href }
  }
  return null
})

const sourceHref = computed(() => {
  return searchStore.getCollectionPath({
    type: props.media.frontendMediaType,
    collectionParams: {
      collection: "source",
      source: props.media.source,
    },
  })
})
</script>

<template>
  <VScrollableLine>
    <VSourceCreatorButton
      v-if="creator"
      :title="creator.name"
      :href="creator.href"
      icon-name="person"
    />
    <VSourceCreatorButton
      :href="sourceHref"
      icon-name="institution"
      :title="media.sourceName"
    />
  </VScrollableLine>
</template>
