<script setup lang="ts">
import { inject, ref, computed, watch, useAttrs } from "vue"

import { warn } from "~/utils/console"

import {
  type VIemGroupContext,
  type VIemGroupFocusContext,
  VItemGroupContextKey,
  VItemGroupFocusContextKey,
} from "~/types/item-group"
import { VPopoverContentContextKey } from "~/types/provides"

import VButton from "~/components/VButton.vue"
import VIcon from "~/components/VIcon/VIcon.vue"

defineOptions({ inheritAttrs: false })

const props = withDefaults(
  defineProps<{
    /**
     * Whether the item is selected/checked.
     */
    selected: boolean
    /**
     * Whether the item is the first in the group.
     */
    isFirst: boolean
    /**
     * To change the underlying component for the VButton,
     * pass `as` prop.
     * @variants 'button', 'VLink'
     */
    as?: "button" | "VLink"
  }>(),
  {
    as: "button",
  }
)

defineEmits<{ click: [] }>()

const attrs = useAttrs()
const injectedFocusContext = inject(VItemGroupFocusContextKey)
const isFocused = ref(false)
const isInPopover = inject(VPopoverContentContextKey, false)
const injectedContextProps = inject(VItemGroupContextKey)

if (!injectedContextProps || !injectedFocusContext) {
  throw new Error(
    "Do not use `VItem` outside of a `VItemGroup`. Use `VButton` instead."
  )
}
const contextProps = injectedContextProps as VIemGroupContext
const focusContext = injectedFocusContext as VIemGroupFocusContext

if (isInPopover && contextProps.bordered) {
  warn("Bordered popover items are not supported")
}

if (attrs.size) {
  warn("The `size` prop should be passed to the parent `VItemGroup` component.")
}

watch(
  () => props.selected,
  (selected, previousSelected) =>
    focusContext.setSelected(selected, previousSelected)
)

const tabIndex = computed(() => {
  // If outside a radiogroup then everything can be tabbable in order
  if (contextProps.type !== "radiogroup") {
    return 0
  }
  // If no items are selected then all can be tabbable to ensure it is possible to enter into the group
  if (
    focusContext.selectedCount.value === 0 &&
    props.isFirst &&
    !focusContext.isGroupFocused.value
  ) {
    return 0
  }
  // If this one is focused then it should be the tabbable item
  if (isFocused.value) {
    return 0
  }
  // If the group is not focused but this is the selected item, then this should be the focusable item when focusing into the group
  if (!focusContext.isGroupFocused.value && props.selected) {
    return 0
  }

  // Otherwise, the item should not be tabbable. The logic above guarantees that at least one other item in the group will be tabbable.
  return -1
})

const splitAttrs = computed(() => {
  const { class: classAttrs, ...rest } = attrs
  return { class: classAttrs, vButtonAttrs: rest }
})
</script>

<template>
  <div
    class="flex"
    :class="[
      contextProps.direction,
      splitAttrs.class,
      {
        [`${contextProps.direction}-bordered`]: contextProps.bordered,
        [`${contextProps.direction}-popover-item`]: isInPopover,
        'border border-default': contextProps.bordered,
        'has-check': contextProps.showCheck,
        'font-semibold': selected && !contextProps.showCheck,
        'bg-transparent':
          selected && contextProps.bordered && contextProps.showCheck,
      },
      isInPopover ? 'px-2' : '',
    ]"
  >
    <VButton
      data-item-group-item
      :as="as"
      class="relative min-w-full justify-between border-0 hover:bg-transparent-hover focus-visible:z-10"
      :class="{
        'w-max': contextProps.direction === 'horizontal',
        '!p-3': contextProps.size === 'small',
        '!p-5 !ps-6': contextProps.size === 'medium',
        'bg-transparent-hover ring-offset-gray-2':
          selected && contextProps.showCheck,
        'text-default': as === 'VLink',
        '!px-2': !contextProps.showCheck,
      }"
      variant="transparent-tx"
      size="disabled"
      :pressed="selected"
      :role="contextProps.type === 'radiogroup' ? 'radio' : 'menuitemcheckbox'"
      :aria-checked="selected"
      :tabindex="tabIndex"
      v-bind="splitAttrs.vButtonAttrs"
      @focus="isFocused = true"
      @blur="isFocused = false"
      @keydown="focusContext.onItemKeyPress"
      @click="$emit('click')"
    >
      <div
        class="flex w-full flex-grow gap-x-2 whitespace-nowrap rounded-sm"
        :class="[`${contextProps.direction}-content`]"
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

<style scoped>
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

.horizontal-bordered {
  @apply border-e border-s-0 border-default;
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
