<template>
  <VAllResultsGrid />
</template>

<script lang="ts">
import { defineComponent } from "vue"

import VAllResultsGrid from "~/components/VSearchResultsGrid/VAllResultsGrid.vue"

export default defineComponent({
  name: "SearchIndex",
  components: { VAllResultsGrid },
})
</script>
