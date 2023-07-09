<template>
  <aside>
    <h2 class="heading-6 md:heading-5 mb-6">
      {{ $t("imageDetails.relatedImages") }}
    </h2>
    <VImageGrid
      :images="media"
      :is-single-page="true"
      :fetch-state="fetchState"
      :image-grid-label="$t('imageDetails.relatedImages').toString()"
    />
  </aside>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { ImageDetail } from "~/types/media"
import type { FetchState } from "~/types/fetch-state"

import VImageGrid from "~/components/VSearchResultsGrid/VImageGrid.vue"

export default defineComponent({
  name: "VRelatedImages",
  components: { VImageGrid },
  props: {
    media: {
      type: Array as PropType<ImageDetail[]>,
      required: true,
    },
    fetchState: {
      type: Object as PropType<FetchState>,
      required: true,
    },
  },
})
</script>
