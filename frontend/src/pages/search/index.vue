<template>
  <VAllResultsGrid />
</template>

<script lang="ts">
import { defineComponent } from "vue"

import { propTypes } from "~/pages/search/search-page.types"

import VAllResultsGrid from "~/components/VSearchResultsGrid/VAllResultsGrid.vue"

export default defineComponent({
  name: "SearchIndex",
  components: { VAllResultsGrid },
  props: propTypes,
})
</script>
