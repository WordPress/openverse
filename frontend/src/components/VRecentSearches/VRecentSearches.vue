<template>
  <div
    class="flex flex-col rounded-sm bg-white"
    :class="{ 'border border-dark-charcoal-20 p-2 shadow-el-2': bordered }"
    data-testid="recent-searches"
  >
    <div
      class="flex h-10 flex-row items-center justify-between ps-3"
      :class="{ 'pe-1': !bordered }"
    >
      <!-- Left margin to align with the text of recent searches. -->
      <span class="category">
        {{ $t("recentSearches.heading") }}
      </span>
      <VButton
        v-show="entries.length"
        variant="transparent-gray"
        class="label-bold"
        size="small"
        :aria-label="$t('recentSearches.clear.label')"
        @click="handleClear()"
      >
        {{ $t("recentSearches.clear.text") }}
      </VButton>
    </div>

    <ul
      v-if="entries.length"
      id="recent-searches-list"
      role="listbox"
      :aria-label="$t('recentSearches.heading')"
    >
      <!-- eslint-disable vuejs-accessibility/interactive-supports-focus Combobox descendants only have visual focus. -->
      <!-- eslint-disable vuejs-accessibility/click-events-have-key-events Key events handled by input field of combobox. -->
      <li
        v-for="(entry, idx) in entries"
        :id="`option-${idx}`"
        :key="entry"
        role="option"
        class="group/entry label-regular flex h-10 flex-row items-center gap-2 rounded-sm border-1.5 pe-1 ps-2 hover:bg-dark-charcoal-10"
        :class="idx === selectedIdx ? 'border-pink' : 'border-tx'"
        :aria-selected="idx === selectedIdx"
        @click="handleClick(idx)"
      >
        <VIcon name="search" />
        {{ entry }}
        <VIconButton
          variant="transparent-gray"
          :icon-props="{ name: 'close-small' }"
          size="small"
          :label="$t('recentSearches.clearSingle.label', { entry })"
          class="ms-auto group-hover/entry:flex"
          :class="{ hidden: bordered }"
          @click.stop="handleClear(entry)"
          @keydown.tab.exact="handleTab(idx)"
        />
      </li>
      <!-- eslint-enable -->
    </ul>
    <span
      v-else
      class="description-regular flex h-10 flex-row items-center ps-3"
      :class="{ 'pe-1': !bordered }"
    >
      {{ $t("recentSearches.none") }}
    </span>

    <span
      class="mt-auto p-3 text-sm leading-close text-dark-charcoal-70 lg:leading-snug"
    >
      {{ $t("recentSearches.disclaimer") }}
    </span>
  </div>
</template>

<script lang="ts">
import { defineComponent, type PropType } from "vue"

import { defineEvent } from "~/types/emits"

import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"
import VIconButton from "~/components/VIconButton/VIconButton.vue"

/**
 * List the recent searches of the user allowing them to go back to a previous
 * search. These searches are saved locally and never shared with the server.
 */
export default defineComponent({
  name: "VRecentSearches",
  components: { VIconButton, VIcon, VButton },
  props: {
    /**
     * the list of saved past searches
     */
    entries: {
      type: Array as PropType<string[]>,
      default: () => [],
    },
    /**
     * the index of the currently selected entry
     */
    selectedIdx: {
      type: Number,
    },
    /**
     * the desktop popover is bordered, and the mobile element is not
     */
    bordered: {
      type: Boolean,
      default: true,
    },
  },
  emits: {
    select: defineEvent<[number]>(),
    clear: defineEvent<[string?]>(),
    "last-tab": defineEvent(),
  },
  setup(props, { emit }) {
    const handleClick = (idx: number) => {
      emit("select", idx)
    }
    const handleClear = (entry?: string) => {
      emit("clear", entry)
    }
    const handleTab = (idx: number) => {
      if (idx === props.entries.length - 1) {
        emit("last-tab")
      }
    }

    return {
      handleClick,
      handleClear,
      handleTab,
    }
  },
})
</script>
