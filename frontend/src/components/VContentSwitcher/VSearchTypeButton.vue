<template>
  <VButton
    class="group h-12 flex-shrink-0 gap-2"
    :class="showLabel ? 'w-auto gap-2 px-3' : 'w-12'"
    variant="action-menu"
    size="disabled"
    :aria-label="$t('search-type.select-label', { type: label })"
    v-bind="$attrs"
    @click="$emit('click')"
  >
    <VIcon :icon-path="icon" />
    <template v-if="showLabel">
      <span class="label-regular block truncate text-start">{{ label }}</span>
      <VIcon :icon-path="caretDownIcon" />
    </template>
  </VButton>
</template>
<script lang="ts">
import { defineComponent, PropType } from "vue"

import type { SearchType } from "~/constants/media"

import { warn } from "~/utils/console"

import VIcon from "~/components/VIcon/VIcon.vue"
import VButton from "~/components/VButton.vue"

import caretDownIcon from "~/assets/icons/caret-down.svg"

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
  setup(_, { attrs }) {
    if (!attrs["aria-haspopup"] || attrs["aria-expanded"] === undefined) {
      warn(
        "You should provide `aria-haspopup` and `aria-expanded` props to VSearchTypeButton."
      )
    }

    return {
      caretDownIcon,
    }
  },
})
</script>
