<template>
  <VAudioCollection
    :results="results"
    :is-related="false"
    :fetch-state="fetchState"
    :collection-label="collectionLabel"
  />
</template>

<script lang="ts">
import { computed, defineComponent, PropType } from "vue"

import { useSearchStore } from "~/stores/search"
import { useI18n } from "~/composables/use-i18n"
import type { AudioDetail } from "~/types/media"
import type { FetchingError, FetchState } from "~/types/fetch-state"

import VAudioCollection from "~/components/VSearchResultsGrid/VAudioCollection.vue"

export default defineComponent({
  name: "AudioSearch",
  components: {
    VAudioCollection,
  },
  props: {
    results: {
      type: Array as PropType<AudioDetail[]>,
      required: true,
    },
    fetchState: {
      type: Object as PropType<FetchState<FetchingError>>,
      required: true,
    },
  },
  setup() {
    const i18n = useI18n()

    const collectionLabel = computed(() => {
      const query = useSearchStore().searchTerm

      return i18n.t("browsePage.aria.results", { query }).toString()
    })

    return {
      collectionLabel,
    }
  },
})
</script>
