<script setup lang="ts">
import { useI18n } from "#imports"

import { computed } from "vue"

import { useSearchStore } from "~/stores/search"

import VButton from "~/components/VButton.vue"
import VFilterIconOrCounter from "~/components/VHeader/VFilterIconOrCounter.vue"

withDefaults(
  defineProps<{
    pressed?: boolean
    disabled?: boolean
  }>(),
  {
    pressed: false,
    disabled: false,
  }
)

defineEmits<{
  toggle: []
}>()

const { t } = useI18n({ useScope: "global" })
const searchStore = useSearchStore()
const filterCount = computed(() => searchStore.appliedFilterCount)

const textLabel = computed(() => t("header.filterButton.simple"))
const ariaLabel = computed(() =>
  t("header.filterButton.withCount", { count: filterCount.value })
)
</script>

<template>
  <VButton
    id="filter-button"
    :variant="pressed ? 'filled-dark' : 'bordered-white'"
    size="disabled"
    class="label-regular h-12 w-12 gap-x-2 self-center xl:w-auto xl:pe-4 xl:ps-3"
    :pressed="pressed"
    :disabled="disabled"
    aria-controls="filters"
    :aria-label="ariaLabel"
    @click="$emit('toggle')"
  >
    <VFilterIconOrCounter
      :applied-filter-count="filterCount"
      :pressed="pressed"
    />
    <span class="hidden xl:inline-block">{{ textLabel }}</span>
  </VButton>
</template>
