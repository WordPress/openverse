<template>
  <VAudioCollection
    :results="results"
    :is-related="false"
    :fetch-state="fetchState"
    :collection-label="`${$t('browsePage.aria.results', {
      query: searchTerm,
    })}`"
  />
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { useMediaStore } from "~/stores/media"
import type { FetchState } from "~/types/fetch-state"

import VAudioCollection from "~/components/VSearchResultsGrid/VAudioCollection.vue"

import type { NuxtError } from "@nuxt/types"

export default defineComponent({
  name: "AudioSearch",
  components: {
    VAudioCollection,
  },
  props: {
    searchTerm: {
      type: String,
      required: true,
    },
    fetchState: {
      type: Object as PropType<FetchState<NuxtError> | FetchState>,
      required: true,
    },
  },
  setup() {
    const mediaStore = useMediaStore()

    const results = computed(() => mediaStore.resultItems.audio)

    return { results }
  },
})
</script>
