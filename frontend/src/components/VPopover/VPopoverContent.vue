<script setup lang="ts">
import { provide, ref, toRefs, useAttrs } from "vue"

import { usePopoverContent } from "~/composables/use-popover-content"

import type { ZIndex } from "~/constants/z-indices"

import { VPopoverContentContextKey } from "~/types/provides"

import type { Placement, Strategy } from "@floating-ui/dom"
import type { SetupContext } from "vue"

const props = withDefaults(
  defineProps<{
    visible: boolean
    hide: () => void
    hideOnEsc?: boolean
    hideOnClickOutside?: boolean
    autoFocusOnShow?: boolean
    autoFocusOnHide?: boolean
    triggerElement: HTMLElement | null
    placement?: Placement
    strategy?: Strategy
    zIndex: ZIndex
    clippable?: boolean
    trapFocus?: boolean
  }>(),
  {
    hideOnEsc: true,
    hideOnClickOutside: true,
    autoFocusOnShow: true,
    autoFocusOnHide: true,
    placement: "bottom-end",
    strategy: "absolute",
    clippable: false,
    trapFocus: true,
  }
)

/**
 * This is the only documented emitted event but in reality we pass through `$listeners`
 * to the underlying element so anything and everything is emitted. `@keydown` is the
 * only one this component overrides and controls (but ultimately still emits).
 */
const emit = defineEmits<{ keydown: []; blur: [] }>()

const attrs = useAttrs()

provide(VPopoverContentContextKey, true)

const propsRefs = toRefs(props)
const popoverRef = ref<HTMLElement | null>(null)

const { onKeyDown, onBlur, heightProperties, style } = usePopoverContent({
  popoverRef,
  popoverPropsRefs: propsRefs,
  emit: emit as SetupContext["emit"],
  attrs,
})
</script>

<template>
  <div
    v-show="visible"
    ref="popoverRef"
    role="dialog"
    aria-modal="true"
    class="popover-content w-max-content absolute left-0 top-0 overflow-y-auto overflow-x-hidden rounded-sm border border-default bg-overlay shadow"
    :class="`z-${zIndex}`"
    :style="{ ...heightProperties, ...style }"
    :tabindex="-1"
    :aria-hidden="!visible"
    @blur="onBlur"
    @keydown="onKeyDown"
  >
    <slot />
  </div>
</template>

<style>
.popover-content {
  height: var(--popover-height, auto);
}
</style>
