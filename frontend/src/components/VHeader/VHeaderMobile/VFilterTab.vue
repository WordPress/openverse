<script setup lang="ts">
import VFilterIconOrCounter from "~/components/VHeader/VFilterIconOrCounter.vue"
import VTab from "~/components/VTabs/VTab.vue"

withDefaults(
  defineProps<{
    /**
     * The number of filters that are currently applied.
     */
    appliedFilterCount?: number
  }>(),
  {
    appliedFilterCount: 0,
  }
)
</script>

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
