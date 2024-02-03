<template>
  <div
    class="flex flex-col gap-1 rounded-sm border bg-white"
    :class="bordered ? 'border-dark-charcoal-20 p-4 shadow-el-2' : 'border-tx'"
    data-testid="recent-searches"
  >
    <div
      class="flex flex-row items-center justify-between py-2"
      :class="{ 'pe-2': !bordered }"
    >
      <!-- Left margin to align with the text of recent searches. -->
      <span class="category mx-2 my-1">
        {{ t("recentSearches.heading") }}
      </span>
      <VButton
        v-show="entries.length"
        variant="transparent-gray"
        class="label-bold"
        size="small"
        :aria-label="t('recentSearches.clear.label')"
        @click="handleClear"
      >
        {{ t("recentSearches.clear.text") }}
      </VButton>
    </div>

    <ul
      v-if="entries.length"
      id="recent-searches-list"
      role="listbox"
      :aria-label="t('recentSearches.heading')"
    >
      <!-- eslint-disable vuejs-accessibility/interactive-supports-focus Combobox descendants only have visual focus. -->
      <!-- eslint-disable vuejs-accessibility/click-events-have-key-events Key events handled by input field of combobox. -->
      <li
        v-for="(entry, idx) in entries"
        :id="`option-${idx}`"
        :key="idx"
        role="option"
        class="description-regular my-1 rounded-sm border-1.5 p-2 hover:bg-dark-charcoal-10"
        :class="idx === selectedIdx ? 'border-pink' : 'border-tx'"
        :aria-selected="idx === selectedIdx"
        @click="handleClick(idx)"
      >
        {{ entry }}
      </li>
      <!-- eslint-enable -->
    </ul>
    <span v-else class="description-regular mx-2 my-3">
      {{ t("recentSearches.none") }}
    </span>

    <span class="caption-regular mx-2 my-3 text-dark-charcoal-70">
      {{ t("recentSearches.disclaimer") }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { useNuxtApp } from "#imports"

import VButton from "~/components/VButton.vue"

/**
 * List the recent searches of the user allowing them to go back to a previous
 * search. These searches are saved locally and never shared with the server.
 */
withDefaults(
  defineProps<{
    /**
     * the list of saved past searches
     */
    entries?: string[]
    /**
     * the index of the currently selected entry
     */
    selectedIdx?: number
    /**
     * the desktop popover is bordered, and the mobile element is not
     */
    bordered?: boolean
  }>(),
  {
    entries: () => [] as string[],
    bordered: true,
  }
)
const emit = defineEmits<{
  select: [number]
  clear: []
}>()

const {
  $i18n: { t },
} = useNuxtApp()
const handleClick = (idx: number) => {
  emit("select", idx)
}
const handleClear = () => {
  emit("clear")
}
</script>
