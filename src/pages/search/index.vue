<template>
  <VAllResultsGrid />
</template>

<script lang="ts">
import { defineComponent, useMeta } from "@nuxtjs/composition-api"

import { propTypes } from "~/pages/search/search-page.types"
import { useFeatureFlagStore } from "~/stores/feature-flag"

import VAllResultsGrid from "~/components/VAllResultsGrid/VAllResultsGrid.vue"

export default defineComponent({
  name: "SearchIndex",
  components: { VAllResultsGrid },
  props: propTypes,
  setup(props) {
    const featureFlagStore = useFeatureFlagStore()

    useMeta({
      title: `${props.searchTerm} | Openverse`,
      meta: featureFlagStore.isOn("new_header")
        ? [{ hid: "robots", name: "robots", content: "all" }]
        : undefined,
    })
  },
  head: {},
})
</script>
