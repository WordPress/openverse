<template>
  <aside v-if="showRelated">
    <h2 class="heading-6 md:heading-5 mb-6">
      {{ $t("imageDetails.relatedImages") }}
    </h2>
    <VImageCollection
      kind="related"
      :results="media"
      :collection-label="$t('imageDetails.relatedImages').toString()"
      class="pt-2 sm:pt-0"
    />
  </aside>
</template>

<script lang="ts">
import { computed, defineComponent, watch } from "vue"
import { useRoute } from "@nuxtjs/composition-api"

import type { ImageDetail } from "~/types/media"
import { useRelatedMediaStore } from "~/stores/media/related-media"

import VImageCollection from "~/components/VSearchResultsGrid/VImageCollection.vue"

export default defineComponent({
  name: "VRelatedImages",
  components: { VImageCollection },
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

    return {
      showRelated,

      media,
    }
  },
})
</script>
