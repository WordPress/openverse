<script setup lang="ts">
/**
 * This is the search type switcher button that appears in the header or the homepage search bar.
 */
import { useAttrs } from "vue"

import type { SearchType } from "~/constants/media"

import { warn } from "~/utils/console"

import { useHydrating } from "~/composables/use-hydrating"

import VIcon from "~/components/VIcon/VIcon.vue"
import VButton from "~/components/VButton.vue"

withDefaults(
  defineProps<{
    /**
     * Whether to show the text label and the chevron down.
     */
    showLabel?: boolean
    searchType: SearchType
    icon: string
    label: string
  }>(),
  {
    showLabel: false,
  }
)

defineEmits<{ click: [] }>()

const attrs = useAttrs()
if (!attrs["aria-haspopup"] || attrs["aria-expanded"] === undefined) {
  warn(
    "You should provide `aria-haspopup` and `aria-expanded` props to VSearchTypeButton."
  )
}
const { doneHydrating } = useHydrating()
</script>

<template>
  <VButton
    class="min-w-12 gap-x-2"
    :class="{ '!px-3': showLabel }"
    variant="bordered-white"
    :icon-only="!showLabel"
    :disabled="!doneHydrating"
    size="large"
    :aria-label="$t('searchType.selectLabel', { type: label })"
    @click="$emit('click')"
  >
    <VIcon :name="searchType" />
    <template v-if="showLabel">
      <span
        class="label-regular block max-w-30 flex-none truncate text-start"
        >{{ label }}</span
      >
      <VIcon name="caret-down" />
    </template>
  </VButton>
</template>
