<template>
  <VTab
    id="filters"
    size="medium"
    class="gap-x-2"
    :aria-label="
      $t('header.filterButton.withCount', { count: appliedFilterCount })
    "
  >
    <VFilterIconOrCounter :applied-filter-count="appliedFilterCount" />
    <h2 class="label-regular">{{ $t("filters.title") }}</h2>
  </VTab>
</template>
<script lang="ts">
import VFilterIconOrCounter from "~/components/VHeader/VFilterIconOrCounter.vue"
import VTab from "~/components/VTabs/VTab.vue"

export default {
  name: "VFilterTab",
  components: { VFilterIconOrCounter, VTab },
  props: {
    appliedFilterCount: {
      type: Number,
      default: 0,
    },
  },
}
</script>
