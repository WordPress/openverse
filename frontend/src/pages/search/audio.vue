<template>
  <VAudioCollection
    :results="results"
    kind="search"
    :fetch-state="fetchState"
    :collection-label="collectionLabel"
  />
</template>

<script lang="ts">
import { defineNuxtComponent, useI18n } from "#imports"

import { computed } from "vue"

import { useSearchStore } from "~/stores/search"

import { useMediaStore } from "~/stores/media"

import VAudioCollection from "~/components/VSearchResultsGrid/VAudioCollection.vue"

export default defineNuxtComponent({
  name: "AudioSearch",
  components: {
    VAudioCollection,
  },
  setup() {
    const i18n = useI18n()
    const mediaStore = useMediaStore()
    const searchStore = useSearchStore()

    const results = computed(() => mediaStore.resultItems["audio"])
    const fetchState = computed(() => mediaStore.fetchState)

    const collectionLabel = computed(() => {
      const query = searchStore.searchTerm

      return i18n.t("browsePage.aria.results", { query })
    })

    return {
      results,
      fetchState,
      collectionLabel,
    }
  },
})
</script>
