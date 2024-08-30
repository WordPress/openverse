<script setup lang="ts">
import { ref, watch, toRefs, onBeforeUnmount } from "vue"

import type { ZIndex } from "~/constants/z-indices"

import { useFloatingUi } from "~/composables/use-floating-ui"
import { hasFocusWithin } from "~/utils/reakit-utils/focus"

import VIconButton from "~/components/VIconButton/VIconButton.vue"

import type { Placement, Strategy } from "@floating-ui/dom"

const props = withDefaults(
  defineProps<{
    /**
     * The placement of the tooltip relative to the trigger. Should be one of the options
     * for `placement` passed to floating-ui.
     *
     * @see https://floating-ui.com/docs/tutorial#placements
     */
    placement?: Placement
    /**
     * The positioning strategy of the tooltip. If your reference element is in a fixed container
     * use the fixed strategy; otherwise use the default, absolute strategy.
     *
     * @see https://floating-ui.com/docs/computeposition#strategy
     */
    strategy?: Strategy
    /**
     * The id of the element labelling the popover content.
     * The owning element must have `aria-describedby` set to this value.
     */
    describedBy: string
    /**
     * the z-index to apply to the tooltip content
     */
    zIndex?: ZIndex
  }>(),
  {
    placement: "bottom",
    strategy: "absolute",
    zIndex: "popover",
  }
)

const visibleRef = ref(false)
const triggerContainerRef = ref<HTMLElement | null>(null)

const closeIfNeeded = () => {
  if (triggerRef.value && !hasFocusWithin(triggerRef.value)) {
    visibleRef.value = false
  }
}

const open = () => {
  visibleRef.value = true
}

const listeners = {
  mouseover: open,
  mouseout: closeIfNeeded,
  focus: open,
  blur: closeIfNeeded,
}

const setTrigger = (triggerElement: HTMLElement) => {
  triggerRef.value = triggerElement
  for (const [event, listener] of Object.entries(listeners)) {
    triggerElement.addEventListener(event, listener)
  }
}

const triggerRef = ref<HTMLElement | null>(null)
watch(triggerContainerRef, (container) => {
  if (container) {
    setTrigger(container.firstElementChild as HTMLElement)
  }
})

onBeforeUnmount(() => {
  if (triggerRef.value) {
    for (const [event, listener] of Object.entries(listeners)) {
      triggerRef.value.removeEventListener(event, listener)
    }
  }
})

const tooltipRef = ref<HTMLElement | null>(null)
const propsRefs = toRefs(props)

const { style } = useFloatingUi({
  floatingElRef: tooltipRef,
  floatingPropsRefs: {
    placement: propsRefs.placement,
    strategy: propsRefs.strategy,
    clippable: ref(false),
    visible: visibleRef,
    triggerElement: triggerRef,
  },
})

const handleEscape = () => {
  if (visibleRef.value) {
    visibleRef.value = false
  }
}
</script>

<template>
  <div>
    <!-- re: disabled static element interactions rule https://github.com/WordPress/openverse/issues/2906 -->
    <!-- eslint-disable-next-line vuejs-accessibility/click-events-have-key-events, vuejs-accessibility/no-static-element-interactions -->
    <div
      ref="triggerContainerRef"
      class="flex w-min items-stretch whitespace-nowrap"
      @keydown.esc="handleEscape"
    >
      <!--
        @slot The trigger, should be a button 99.99% of the time. If you need custom event handling on the trigger button, ensure bubbling is not prevented or else the tooltip will not open
          @binding {object} a11yProps
          @binding {boolean} visible
      -->
      <slot name="trigger" :open="open">
        <VIconButton
          :label="describedBy"
          :aria-describedby="describedBy"
          variant="bordered-white"
          size="disabled"
          class="h-4 w-4 hover:!border-tx"
          :icon-props="{ name: 'info', size: 4 }"
          @click="open"
        />
      </slot>
    </div>
    <div
      v-show="visibleRef"
      :id="describedBy"
      ref="tooltipRef"
      role="tooltip"
      :class="`z-${zIndex} w-max-content absolute left-0 top-0`"
      :style="{ ...style }"
      :aria-hidden="!visibleRef"
    >
      <slot />
    </div>
  </div>
</template>
