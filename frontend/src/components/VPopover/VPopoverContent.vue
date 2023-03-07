<template>
  <div
    v-show="visible"
    class="h-0 w-0"
    :aria-hidden="!visible"
    v-on="$listeners"
    @keydown="onKeyDown"
  >
    <div
      ref="popoverRef"
      class="popover-content overflow-y-auto overflow-x-hidden rounded-sm border border-light-gray bg-white shadow"
      :class="[`z-${zIndex}`, width]"
      :style="heightProperties"
      :tabindex="-1"
      v-bind="$attrs"
      @blur="onBlur"
    >
      <slot />
    </div>
  </div>
</template>

<script lang="ts">
import {
  defineComponent,
  toRefs,
  ref,
  provide,
  InjectionKey,
  PropType,
} from "vue"

import { usePopoverContent } from "~/composables/use-popover-content"
import { defineEvent } from "~/types/emits"

import { zIndexValidator } from "~/constants/z-indices"

import type { Placement, PositioningStrategy } from "@popperjs/core"

import type { SetupContext } from "vue"

export const VPopoverContentContextKey = Symbol(
  "VPopoverContentContextKey"
) as InjectionKey<boolean>

export default defineComponent({
  name: "VPopoverContent",
  inheritAttrs: false,
  props: {
    visible: {
      type: Boolean,
      required: true,
    },
    hide: {
      type: Function as PropType<() => void>,
      required: true,
    },
    hideOnEsc: {
      type: Boolean,
      default: true,
    },
    hideOnClickOutside: {
      type: Boolean,
      default: true,
    },
    autoFocusOnShow: {
      type: Boolean,
      default: true,
    },
    autoFocusOnHide: {
      type: Boolean,
      default: true,
    },
    triggerElement: {
      type: (process.server
        ? Object
        : HTMLElement) as PropType<HTMLElement | null>,
      required: true,
    },
    placement: {
      type: String as PropType<Placement>,
      default: "bottom-end",
    },
    strategy: {
      type: String as PropType<PositioningStrategy>,
      default: "absolute",
    },
    zIndex: {
      type: [String, Number],
      required: true,
      validator: zIndexValidator,
    },
    clippable: {
      type: Boolean,
      default: false,
    },
    /**
     * Optional Tailwind class for fixed width.
     */
    width: {
      type: String,
    },
  },
  /**
   * This is the only documented emitted event but in reality we pass through `$listeners`
   * to the underlying element so anything and everything is emitted. `@keydown` is the
   * only one this component overrides and controls (but ultimately still emits).
   */
  emits: { keydown: defineEvent(), blur: defineEvent() },
  setup(props, { emit, attrs }) {
    provide(VPopoverContentContextKey, true)

    const propsRefs = toRefs(props)
    const popoverRef = ref<HTMLElement | null>(null)

    const { onKeyDown, onBlur, heightProperties } = usePopoverContent({
      popoverRef,
      popoverPropsRefs: propsRefs,
      emit: emit as SetupContext["emit"],
      attrs,
    })

    return { popoverRef, onKeyDown, onBlur, heightProperties }
  },
})
</script>
<style>
.popover-content {
  height: var(--popover-height, auto);
  scrollbar-gutter: stable;
  overflow-x: hidden;
}
</style>
