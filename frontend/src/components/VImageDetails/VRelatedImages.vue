<template>
  <aside>
    <h2 class="heading-6 md:heading-5 mb-6">
      {{ $t("image-details.related-images") }}
    </h2>
    <VLoadingIcon v-if="fetchState.isFetching" />
    <VImageGrid
      :images="media"
      :is-single-page="true"
      :fetch-state="fetchState"
    />
  </aside>
</template>

<script lang="ts">
import { defineComponent, PropType } from "@nuxtjs/composition-api"

import type { ImageDetail } from "~/types/media"
import type { FetchState } from "~/types/fetch-state"

import VImageGrid from "~/components/VImageGrid/VImageGrid.vue"
import VLoadingIcon from "~/components/LoadingIcon.vue"

export default defineComponent({
  name: "VRelatedImages",
  components: { VImageGrid, VLoadingIcon },
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
