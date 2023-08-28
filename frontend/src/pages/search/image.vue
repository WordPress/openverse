<template>
  <VImageGrid
    :images="results"
    :is-single-page="false"
    :fetch-state="fetchState"
    :image-grid-label="`${$t('browsePage.aria.results', {
      query: searchTerm,
    })}`"
  />
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import type { FetchState } from "~/types/fetch-state"

import { useMediaStore } from "~/stores/media"

import VImageGrid from "~/components/VSearchResultsGrid/VImageGrid.vue"

import type { NuxtError } from "@nuxt/types"

export default defineComponent({
  name: "ImageSearch",
  components: { VImageGrid },
  props: {
    fetchState: {
      type: Object as PropType<FetchState<NuxtError> | FetchState>,
      required: true,
    },
    searchTerm: {
      type: String,
      required: true,
    },
  },
  setup() {
    const mediaStore = useMediaStore()

    const results = computed(() => mediaStore.resultItems.image)

    return { results }
  },
})
</script>
