<template>
  <div
    class="flex"
    :class="{
      [$style[contextProps.direction]]: true,
      [`border border-dark-charcoal-20 ${
        $style[`${contextProps.direction}-bordered`]
      }`]: contextProps.bordered,
      'bg-dark-charcoal-10':
        selected && contextProps.bordered && contextProps.showCheck,
      'px-2': isInPopover,
      'hover:bg-dark-charcoal-10': !isInPopover,
      [$style[`${contextProps.direction}-popover-item`]]: isInPopover,
      'has-check': contextProps.showCheck,
      'font-semibold': selected && !contextProps.showCheck,
    }"
  >
    <VButton
      data-item-group-item
      :as="as"
      class="group relative flex min-w-full justify-between border-0 py-2 hover:bg-dark-charcoal-10 focus:z-10"
      :class="[
        $style[`${contextProps.direction}-button`],
        $style[`${contextProps.size}-button`],
        selected &&
          contextProps.showCheck &&
          'bg-dark-charcoal-10 ring-offset-dark-charcoal-10',
        as === 'VLink' && 'text-dark-charcoal',
        !contextProps.showCheck && 'px-2',
      ]"
      variant="transparent-tx"
      size="disabled"
      :pressed="selected"
      :role="contextProps.type === 'radiogroup' ? 'radio' : 'menuitemcheckbox'"
      :aria-checked="selected"
      :tabindex="tabIndex"
      v-bind="$attrs"
      v-on="$listeners"
      @focus="isFocused = true"
      @blur="isFocused = false"
      @keydown="focusContext.onItemKeyPress"
      @keydown.native="focusContext.onItemKeyPress"
      @click.native="$emit('click')"
    >
      <div
        class="flex w-full flex-grow gap-x-2 whitespace-nowrap rounded-sm"
        :class="[$style[`${contextProps.direction}-content`]]"
      >
        <slot name="default" />
      </div>
      <VIcon
        v-if="
          selected &&
          contextProps.direction === 'vertical' &&
          contextProps.showCheck
        "
        class="absolute"
        :class="contextProps.size === 'small' ? 'end-3' : 'end-5'"
        name="item-indicator"
      />
    </VButton>
  </div>
</template>

<script lang="ts">
import { defineComponent, inject, ref, computed, watch, PropType } from "vue"

import { warn } from "~/utils/console"

import {
  VItemGroupContextKey,
  VItemGroupFocusContextKey,
} from "~/types/item-group"

import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"
import { VPopoverContentContextKey } from "~/components/VPopover/VPopoverContent.vue"

export default defineComponent({
  name: "VItem",
  components: { VButton, VIcon },
  inheritAttrs: false,
  props: {
    /**
     * Whether the item is selected/checked.
     */
    selected: {
      type: Boolean,
      required: true,
    },
    /**
     * Whether the item is the first in the group.
     */
    isFirst: {
      type: Boolean,
      required: true,
    },
    /**
     * To change the underlying component for the VButton,
     * pass `as` prop.
     * @variants 'button', 'VLink'
     */
    as: {
      type: String as PropType<"button" | "VLink">,
      default: "button",
      validator: (val: string) => ["button", "VLink"].includes(val),
    },
  },
  /**
   * Setting `inheritAttrs` to false ensures that the $attrs are only passed to VButton component,
   * and not the outer div. In Vue 3 this will also stops native events such as `click` from
   * going up the tree. Adding `emits` should fix this:
   * https://v3.vuejs.org/guide/migration/v-on-native-modifier-removed.html#_3-x-syntax
   * However, with current Vue 2 setup, if VItem is a link (a or NuxtLink), it is
   * necessary to add native modifier to handle click event: `@click.native='handler'`.
   */
  emits: ["click"],
  setup(props) {
    const focusContext = inject(VItemGroupFocusContextKey)
    const isFocused = ref(false)
    const isInPopover = inject(VPopoverContentContextKey, false)
    const contextProps = inject(VItemGroupContextKey)

    if (!contextProps || !focusContext) {
      throw new Error(
        "Do not use `VItem` outside of a `VItemGroup`. Use `VButton` instead."
      )
    }

    if (isInPopover && contextProps.bordered) {
      warn("Bordered popover items are not supported")
    }

    watch(
      () => props.selected,
      (selected, previousSelected) =>
        focusContext.setSelected(selected, previousSelected)
    )

    const tabIndex = computed(() => {
      // If outside a radiogroup then everything can be tabbable in order
      if (contextProps.type !== "radiogroup") {return 0}
      // If no items are selected then all can be tabbable to ensure it is possible to enter into the group
      if (
        focusContext.selectedCount.value === 0 &&
        props.isFirst &&
        !focusContext.isGroupFocused.value
      )
        {return 0}
      // If this one is focused then it should be the tabbable item
      if (isFocused.value) {return 0}
      // If the group is not focused but this is the selected item, then this should be the focusable item when focusing into the group
      if (!focusContext.isGroupFocused.value && props.selected) {return 0}

      // Otherwise, the item should not be tabbable. The logic above guarantees that at least one other item in the group will be tabbable.
      return -1
    })

    return {
      contextProps,
      isInPopover,
      isFocused,
      tabIndex,
      focusContext,
    }
  },
})
</script>
<style module>
.button:focus {
  @apply z-10;
}

.vertical {
  @apply min-w-max;
}

.vertical-bordered {
  @apply border-b border-t-0;
}

.vertical:first-of-type {
  @apply rounded-se-sm rounded-ss-sm;
}

.vertical-bordered:first-of-type {
  @apply border-t;
}

.vertical:last-of-type {
  @apply rounded-ee-sm rounded-es-sm;
}

.vertical-content {
  @apply flex flex-row items-center;
}

.vertical-popover-item {
  @apply pb-0;
}

.horizontal-button {
  @apply w-max;
}

.horizontal-bordered {
  @apply border-e border-s-0 border-dark-charcoal-20;
}

.horizontal:first-of-type {
  @apply rounded-s-sm;
}

.horizontal-bordered:first-of-type {
  @apply border-s;
}

.horizontal:last-of-type {
  @apply rounded-e-sm;
}

.horizontal-content {
  @apply flex flex-col items-center;
}

.horizontal-popover-item {
  @apply pe-0;
}

.horizontal-popover-item:last-of-type {
  @apply pe-2;
}
.small-button {
  @apply p-3;
}
.medium-button {
  @apply p-5 ps-6;
}
</style>
