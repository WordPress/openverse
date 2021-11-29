<template>
  <div
    class="flex"
    :class="{
      [$style[contextProps.direction]]: true,
      [`border border-dark-charcoal-20 ${
        $style[`${contextProps.direction}-bordered`]
      }`]: contextProps.bordered,
      'bg-dark-charcoal-10': selected && contextProps.bordered,
      'p-2': isInPopover,
      [$style[`${contextProps.direction}-popover-item`]]: isInPopover,
    }"
  >
    <VButton
      data-item-group-item
      class="flex justify-between focus-visible:ring-pink rounded min-w-full"
      :class="[$style.button, $style[`${contextProps.direction}-button`]]"
      variant="grouped"
      size="small"
      :pressed="selected"
      :role="contextProps.type === 'radiogroup' ? 'radio' : 'menuitemcheckbox'"
      :aria-checked="selected"
      :tabindex="tabIndex"
      v-bind="$attrs"
      v-on="$listeners"
      @focus="isFocused = true"
      @blur="isFocused = false"
      @keydown="focusContext.onItemKeyPress"
    >
      <div
        class="flex-grow whitespace-nowrap"
        :class="$style[`${contextProps.direction}-content`]"
      >
        <slot name="default" />
      </div>
      <VIcon
        v-if="!isInPopover && selected && contextProps.direction === 'vertical'"
        :icon-path="check"
      />
    </VButton>
  </div>
</template>

<script>
import {
  defineComponent,
  inject,
  ref,
  computed,
  watch,
} from '@nuxtjs/composition-api'
import check from '~/assets/icons/check.svg'
import VButton from '~/components/VButton.vue'
import VIcon from '~/components/VIcon/VIcon.vue'
import {
  VItemGroupContextKey,
  VItemGroupFocusContextKey,
} from './VItemGroup.vue'
import { VPopoverContentContextKey } from '~/components/VPopover/VPopoverContent.vue'
import { warn } from '~/utils/warn'

export default defineComponent({
  name: 'VItem',
  components: { VButton, VIcon },
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
  },
  setup(props) {
    const focusContext = inject(VItemGroupFocusContextKey)
    const isFocused = ref(false)
    const isInPopover = inject(VPopoverContentContextKey, false)
    const contextProps = inject(VItemGroupContextKey)

    if (isInPopover && contextProps.bordered) {
      warn('Bordered popover items are not supported')
    }

    watch(
      () => props.selected,
      (selected, previousSelected) =>
        focusContext.setSelected(selected, previousSelected)
    )

    const tabIndex = computed(() => {
      // If outside a radiogroup then everything can be tabbable in order
      if (contextProps.type !== 'radiogroup') return 0
      // If no items are selected then all can be tabbable to ensure it is possible to enter into the group
      if (
        focusContext.selectedCount.value === 0 &&
        props.isFirst &&
        !focusContext.isGroupFocused.value
      )
        return 0
      // If this one is focused then it should be the tabbable item
      if (isFocused.value) return 0
      // If the group is not focused but this is the selected item, then this should be the focusable item when focusing into the group
      if (!focusContext.isGroupFocused.value && props.selected) return 0

      // Otherwise the item should not be tabbable. The logic above guarantees that at least one other item in the group will be tabbable.
      return -1
    })

    return {
      check,
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
  @apply border-t-0 border-b;
}

.vertical:first-of-type {
  @apply rounded-t-sm;
}

.vertical-bordered:first-of-type {
  @apply border-t;
}

.vertical:last-of-type {
  @apply rounded-b-sm;
}

.vertical-content {
  @apply flex flex-row;
}

.vertical-popover-item {
  @apply pb-0;
}

.vertical-popover-item:last-of-type {
  @apply pb-2;
}

.horizontal-button {
  @apply w-max;
}

.horizontal-bordered {
  @apply border-s-0 border-e border-dark-charcoal-20;
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
</style>
