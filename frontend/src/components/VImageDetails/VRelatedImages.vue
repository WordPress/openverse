<template>
  <aside v-if="showRelated">
    <h2 class="heading-6 md:heading-5 mb-6">
      {{ $t("imageDetails.relatedImages") }}
    </h2>
    <VImageGrid
      kind="related"
      :results="media"
      :fetch-state="fetchState"
      :image-grid-label="$t('imageDetails.relatedImages')"
    />
  </aside>
</template>

<script lang="ts">
import { useRoute } from "#imports"

import { computed, defineComponent, watch } from "vue"

import type { ImageDetail } from "~/types/media"
import { useRelatedMediaStore } from "~/stores/media/related-media"

import VImageGrid from "~/components/VSearchResultsGrid/VImageGrid.vue"

export default defineComponent({
  name: "VRelatedImages",
  components: { VImageGrid },
  setup() {
    const relatedMediaStore = useRelatedMediaStore()

    const route = useRoute()

    watch(
      route,
      async (newRoute) => {
        if (newRoute.params.id !== relatedMediaStore.mainMediaId) {
          await relatedMediaStore.fetchMedia("image", newRoute.params.id)
        }
      },
      { immediate: true }
    )

    const showRelated = computed(
      () => media.value.length > 0 || relatedMediaStore.fetchState.isFetching
    )

    const media = computed(
      () => (relatedMediaStore.media ?? []) as ImageDetail[]
    )

    const fetchState = computed(() => relatedMediaStore.fetchState)

    return {
      showRelated,

      media,

      fetchState,
    }
  },
})
</script>
