<template>
  <section v-if="showRelated">
    <h2 class="heading-6 lg:heading-6 mb-6">
      {{ $t("audioDetails.relatedAudios") }}
    </h2>
    <VAudioCollection
      :results="media"
      kind="related"
      :collection-label="$t('audioDetails.relatedAudios')"
      class="mb-12"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, toRef, watch } from "vue"

import { useRelatedMediaStore } from "~/stores/media/related-media"

import type { AudioDetail } from "~/types/media"

import VAudioCollection from "~/components/VSearchResultsGrid/VAudioCollection.vue"

const props = defineProps<{
  mediaId: string
}>()

const relatedMediaStore = useRelatedMediaStore()

const media = computed(() => (relatedMediaStore.media ?? []) as AudioDetail[])

const idRef = toRef(props, "mediaId")
watch(
  idRef,
  (newId) => {
    if (newId !== relatedMediaStore.mainMediaId) {
      return relatedMediaStore.fetchMedia("audio", newId)
    }
  },
  { immediate: true }
)

const showRelated = computed(() => media.value.length > 0)
</script>
