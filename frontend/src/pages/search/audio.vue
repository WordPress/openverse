<template>
  <VAudioCollection
    :results="results"
    kind="search"
    :collection-label="collectionLabel"
  />
</template>

<script lang="ts">
import { defineNuxtComponent, useI18n } from "#imports"

import { computed, PropType } from "vue"

import { useSearchStore } from "~/stores/search"

import type { AudioDetail } from "~/types/media"

import VAudioCollection from "~/components/VSearchResultsGrid/VAudioCollection.vue"

export default defineNuxtComponent({
  name: "AudioSearch",
  components: {
    VAudioCollection,
  },
  props: {
    results: {
      type: Array as PropType<AudioDetail[]>,
      required: true,
    },
  },
  setup() {
    const i18n = useI18n({ useScope: "global" })
    const searchStore = useSearchStore()

    const collectionLabel = computed(() => {
      const query = searchStore.searchTerm

      return i18n.t("browsePage.aria.results", { query })
    })

    return {
      collectionLabel,
    }
  },
})
</script>
