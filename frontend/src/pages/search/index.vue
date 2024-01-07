<template>
  <VAllResultsGrid />
</template>

<script lang="ts">
import { defineNuxtComponent } from "#imports"

import VAllResultsGrid from "~/components/VSearchResultsGrid/VAllResultsGrid.vue"

export default defineNuxtComponent({
  name: "SearchIndex",
  components: { VAllResultsGrid },
})
</script>
