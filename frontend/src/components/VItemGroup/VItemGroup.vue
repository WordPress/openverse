<script setup lang="ts">
import { useNuxtApp } from "#imports"

import { provide, ref, readonly } from "vue"

import { keycodes } from "~/constants/key-codes"
import { ensureFocus } from "~/utils/reakit-utils/focus"
import type {
  ItemGroupDirection,
  ItemGroupSize,
  ItemGroupType,
} from "~/types/item-group"
import {
  VItemGroupContextKey,
  VItemGroupFocusContextKey,
} from "~/types/item-group"

const arrows = [
  keycodes.ArrowUp,
  keycodes.ArrowDown,
  keycodes.ArrowLeft,
  keycodes.ArrowRight,
]

const props = withDefaults(
  defineProps<{
    /**
     * The direction to render the items in.
     *
     * @default 'vertical'
     */
    direction?: ItemGroupDirection
    /**
     * Whether to render a bordered, separated list of items. When false each
     * item will have whitespace separating them instead of borders.
     *
     * @default true
     */
    bordered?: boolean
    /**
     * The type of item group and item to render. This directly affects the `role` attribute
     * of the container and the items themselves.
     *
     * `menu` should be used when providing a menu of independent options.
     *
     * @see https://www.w3.org/TR/wai-aria-1.1/#menu
     *
     * `radiogroup` should be used when providing a menu of options where only one can be selected at a time.
     *
     * @see https://www.w3.org/TR/wai-aria-1.1/#radiogroup
     */
    type?: ItemGroupType
    /**
     * Size of the item group corresponds to the size of the component.
     */
    size?: ItemGroupSize
    /**
     * Whether to show a checkmark when an item is selected.
     */
    showCheck?: boolean
  }>(),
  {
    direction: "vertical",
    bordered: true,
    type: "menu",
    size: "small",
    showCheck: true,
  }
)

const nodeRef = ref<HTMLElement | null>(null)
const isFocused = ref(false)
provide(VItemGroupContextKey, props)

const i18n = useNuxtApp().$i18n

/**
 * When the item group is horizontal, we need to "reverse" the behavior of the left and right arrow keys for RTL locales
 * because the DOM order gets reversed to be opposite the visual order relative to left/right movement.
 *
 * For vertical locales it should remain the same.
 * @param ltr
 * @param rtl
 */
const resolveArrow = (ltr: string, rtl: string) => {
  return i18n.localeProperties.value.dir === "rtl" &&
    props.direction === "horizontal"
    ? rtl
    : ltr
}

const onItemKeyPress = (event: KeyboardEvent): undefined | number => {
  if (!(arrows as string[]).includes(event.key) || !nodeRef.value) {
    return
  }

  event.preventDefault()

  const target = event.target

  // While VItem ultimately renders a button at the moment, that could change in the future, so using a data attribute selector makes it more flexible for the future
  const items = Array.from<HTMLElement>(
    nodeRef.value?.querySelectorAll("[data-item-group-item]")
  )

  const targetIndex = items.findIndex((item) => item === target)

  switch (event.key) {
    case keycodes.ArrowUp:
    case resolveArrow(keycodes.ArrowLeft, keycodes.ArrowRight): {
      if (targetIndex === 0) {
        return ensureFocus(items[items.length - 1])
      }
      return ensureFocus(items[targetIndex - 1])
    }
    case keycodes.ArrowDown:
    case resolveArrow(keycodes.ArrowRight, keycodes.ArrowLeft): {
      if (targetIndex === items.length - 1) {
        return ensureFocus(items[0])
      }
      return ensureFocus(items[targetIndex + 1])
    }
    default: {
      return
    }
  }
}

const selectedCount = ref(0)

/**
 * @param selected
 * @param previousSelected
 */
const setSelected = (selected: boolean, previousSelected: boolean) => {
  if (previousSelected && !selected) {
    selectedCount.value -= 1
  }
  if (!previousSelected && selected) {
    selectedCount.value += 1
  }
}

const focusContext = {
  isGroupFocused: readonly(isFocused),
  onItemKeyPress,
  selectedCount: readonly(selectedCount),
  setSelected,
}

provide(VItemGroupFocusContextKey, focusContext)
</script>

<template>
  <div
    ref="nodeRef"
    class="flex w-full"
    :role="type"
    :class="{
      'flex-col': direction === 'vertical',
      'flex-row': direction !== 'vertical',
      'flex-wrap': direction === 'columns',
    }"
    @focusin="isFocused = true"
    @focusout="isFocused = false"
  >
    <!--
      @slot The items in the item group. Must include some `VItem`s but can
      include additional elements as-needed.
    -->
    <slot name="default" />
  </div>
</template>
