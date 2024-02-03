<template>
  <VButton
    class="gap-x-2"
    :class="{ '!px-3': showLabel }"
    variant="bordered-white"
    :disabled="!doneHydrating"
    :icon-only="!showLabel"
    size="large"
    :aria-label="t('searchType.selectLabel', { type: label })"
    v-bind="attrs"
    @click="emit('click')"
  >
    <VIcon :name="searchType" :size="6" />
    <template v-if="showLabel">
      <span class="label-regular block flex-shrink-0 truncate text-start">{{
        label
      }}</span>
      <VIcon name="caret-down" />
    </template>
  </VButton>
</template>
<script setup lang="ts">
import { useNuxtApp } from "#imports"

import { useAttrs } from "vue"

import type { SearchType } from "~/constants/media"

import { warn } from "~/utils/console"

import { useHydrating } from "~/composables/use-hydrating"

import VIcon from "~/components/VIcon/VIcon.vue"
import VButton from "~/components/VButton.vue"

/**
 * This is the search type switcher button that appears in the header or the homepage search bar.
 */
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

const emit = defineEmits(["click"])
const attrs = useAttrs()
if (!attrs["aria-haspopup"] || attrs["aria-expanded"] === undefined) {
  warn(
    "You should provide `aria-haspopup` and `aria-expanded` props to VSearchTypeButton."
  )
}
const { doneHydrating } = useHydrating()
const {
  $i18n: { t },
} = useNuxtApp()
</script>
