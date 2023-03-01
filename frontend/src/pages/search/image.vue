<template>
  <VImageGrid
    :images="results"
    :is-single-page="false"
    :fetch-state="fetchState"
  />
</template>

<script lang="ts">
import { computed, defineComponent } from "vue"
import { useMeta } from "@nuxtjs/composition-api"

import { propTypes } from "~/pages/search/search-page.types"

import VImageGrid from "~/components/VImageGrid/VImageGrid.vue"

export default defineComponent({
  name: "ImageSearch",
  components: { VImageGrid },
  props: propTypes,
  setup(props) {
    useMeta({
      title: `${props.searchTerm} | Openverse`,
      meta: [{ hid: "robots", name: "robots", content: "all" }],
    })

    const results = computed(() => props.resultItems.image)

    return { results }
  },
  head: {},
})
</script>
