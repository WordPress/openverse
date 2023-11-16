<template>
  <div
    v-show="visible"
    ref="popoverRef"
    role="dialog"
    aria-modal="true"
    class="popover-content w-max-content absolute left-0 top-0 overflow-y-auto overflow-x-hidden rounded-sm border border-light-gray bg-white shadow"
    :class="[`z-${zIndex}`, width]"
    :style="{ ...heightProperties, ...style }"
    :tabindex="-1"
    :aria-hidden="!visible"
    @blur="onBlur"
    @keydown="onKeyDown"
  >
    <slot />
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

import type { Placement, Strategy } from "@floating-ui/dom"

import type { SetupContext } from "vue"

export const VPopoverContentContextKey = Symbol(
  "VPopoverContentContextKey"
) as InjectionKey<boolean>

export default defineComponent({
  name: "VPopoverContent",
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
      type: String as PropType<Strategy>,
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
    trapFocus: {
      type: Boolean,
      default: true,
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

    const { onKeyDown, onBlur, heightProperties, style } = usePopoverContent({
      popoverRef,
      popoverPropsRefs: propsRefs,
      emit: emit as SetupContext["emit"],
      attrs,
    })

    return { popoverRef, onKeyDown, onBlur, heightProperties, style }
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
