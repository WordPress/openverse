<template>
  <section v-if="showRelated">
    <h2 class="heading-6 lg:heading-6 mb-6">
      {{ $t("audioDetails.relatedAudios") }}
    </h2>
    <VAudioCollection
      :results="media"
      :fetch-state="fetchState"
      kind="related"
      :collection-label="$t('audioDetails.relatedAudios').toString()"
      class="mb-12"
    />
  </section>
</template>

<script lang="ts">
import { useRoute } from "#imports"

import { computed, defineComponent, watch } from "vue"

import { useRelatedMediaStore } from "~/stores/media/related-media"

import { defineEvent } from "~/types/emits"
import type { AudioDetail } from "~/types/media"
import type { AudioInteractionData } from "~/types/analytics"

import VAudioCollection from "~/components/VSearchResultsGrid/VAudioCollection.vue"

export default defineComponent({
  name: "VRelatedAudio",
  components: { VAudioCollection },
  emits: {
    interacted: defineEvent<[Omit<AudioInteractionData, "component">]>(),
  },
  setup() {
    const relatedMediaStore = useRelatedMediaStore()

    const route = useRoute()

    const media = computed(
      () => (relatedMediaStore.media ?? []) as AudioDetail[]
    )
    watch(
      () => route.params.id,
      async (newRouteIdParam) => {
        const newRouteId = Array.isArray(newRouteIdParam)
          ? newRouteIdParam[0]
          : newRouteIdParam
        if (newRouteId !== relatedMediaStore.mainMediaId) {
          await relatedMediaStore.fetchMedia("audio", newRouteId)
        }
      },
      { immediate: true }
    )

    const showRelated = computed(
      () => media.value.length > 0 || relatedMediaStore.fetchState.isFetching
    )

    const fetchState = computed(() => relatedMediaStore.fetchState)

    return {
      media,
      showRelated,
      fetchState,
    }
  },
})
</script>
