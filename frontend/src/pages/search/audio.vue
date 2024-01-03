<template>
  <VAudioCollection
    :results="results"
    kind="search"
    :fetch-state="fetchState"
    :collection-label="collectionLabel"
  />
</template>

<script lang="ts">
import { defineNuxtComponent } from "#imports"

import { computed, PropType } from "vue"

import { useSearchStore } from "~/stores/search"
import { useNuxtI18n } from "~/composables/use-i18n"
import type { AudioDetail } from "~/types/media"
import type { FetchState } from "~/types/fetch-state"

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
    fetchState: {
      type: Object as PropType<FetchState>,
      required: true,
    },
  },
  setup() {
    const i18n = useNuxtI18n()

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
