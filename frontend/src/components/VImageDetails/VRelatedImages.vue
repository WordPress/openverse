<template>
  <aside v-if="showRelated">
    <h2 class="heading-6 md:heading-5 mb-6">
      {{ $t("imageDetails.relatedImages") }}
    </h2>
    <VImageGrid
      kind="related"
      :results="media"
      :related-to="mediaId"
      :image-grid-label="$t('imageDetails.relatedImages')"
    />
  </aside>
</template>

<script setup lang="ts">
import { computed, toRef, watch } from "vue"

import { useRelatedMediaStore } from "~/stores/media/related-media"

import type { ImageDetail } from "~/types/media"

import VImageGrid from "~/components/VSearchResultsGrid/VImageGrid.vue"

const props = defineProps<{
  mediaId: string
}>()
const relatedMediaStore = useRelatedMediaStore()
const mediaId = toRef(props, "mediaId")

watch(
  mediaId,
  async (newMediaId) => {
    await relatedMediaStore.fetchMedia("image", newMediaId)
  },
  { immediate: true }
)

const showRelated = computed(
  () => media.value.length > 0 || relatedMediaStore.fetchState.isFetching
)

const media = computed(() => relatedMediaStore.media as ImageDetail[])
</script>
