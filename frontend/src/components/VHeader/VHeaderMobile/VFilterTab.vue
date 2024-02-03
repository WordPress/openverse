<template>
  <VTab id="filters" size="medium" class="gap-x-2">
    <VFilterIconOrCounter :applied-filter-count="appliedFilterCount" />
    <h2 class="label-regular">{{ t("filters.title") }}</h2>
  </VTab>
</template>
<script setup lang="ts">
import { useNuxtApp } from "#imports"

import VFilterIconOrCounter from "~/components/VHeader/VFilterIconOrCounter.vue"
import VTab from "~/components/VTabs/VTab.vue"

withDefaults(
  defineProps<{
    appliedFilterCount: number
  }>(),
  {
    appliedFilterCount: 0,
  }
)

const {
  $i18n: { t },
} = useNuxtApp()
</script>
