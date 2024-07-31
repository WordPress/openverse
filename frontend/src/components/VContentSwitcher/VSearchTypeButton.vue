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

<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { SearchType } from "~/constants/media"

import { warn } from "~/utils/console"

import { defineEvent } from "~/types/emits"

import { useHydrating } from "~/composables/use-hydrating"

import VIcon from "~/components/VIcon/VIcon.vue"
import VButton from "~/components/VButton.vue"

/**
 * This is the search type switcher button that appears in the header or the homepage search bar.
 */
export default defineComponent({
  name: "VSearchTypeButton",
  components: { VButton, VIcon },
  props: {
    /**
     * Whether to show the text label and the chevron down.
     */
    showLabel: {
      type: Boolean,
      default: false,
    },
    searchType: {
      type: String as PropType<SearchType>,
      required: true,
    },
    icon: {
      type: String,
      required: true,
    },
    label: {
      type: String,
      required: true,
    },
  },
  emits: {
    click: defineEvent(),
  },
  setup(_, { attrs }) {
    if (!attrs["aria-haspopup"] || attrs["aria-expanded"] === undefined) {
      warn(
        "You should provide `aria-haspopup` and `aria-expanded` props to VSearchTypeButton."
      )
    }
    const { doneHydrating } = useHydrating()

    return {
      doneHydrating,
    }
  },
})
</script>
