<script setup lang="ts">
/**
 * NB: Most of these technically default to `undefined` so that the underlying `VPopoverContent`
 * default for each of them can take over.
 */
import { ref, computed, SetupContext } from "vue"

import { zIndexValidator } from "~/constants/z-indices"

import { useDialogControl } from "~/composables/use-dialog-control"

import VPopoverContent from "~/components/VPopover/VPopoverContent.vue"

import type { Placement, Strategy } from "@floating-ui/dom"

const props = withDefaults(
  defineProps<{
    /**
     * Whether the popover should show when the trigger is hovered on.
     */
    activateOnHover?: boolean
    /**
     * Whether the popover should hide when the <kbd>Escape</kbd> key is pressed.
     *
     * @default true
     */
    hideOnEsc?: boolean
    /**
     * Whether the popover should hide when a click happens outside the popover content,
     * excluding the trigger. When the trigger is clicked and the popover is open, nothing
     * will happen.
     *
     * @default true
     */
    hideOnClickOutside?: boolean
    /**
     * Whether the popover content should automatically receive focus when the popover
     * opens.
     *
     * @default true
     */
    autoFocusOnShow?: boolean
    /**
     * Whether the trigger should automatically receive focus when the popover closes.
     *
     * @default true
     */
    autoFocusOnHide?: boolean
    /**
     * The placement of the popover relative to the trigger. Should be one of the options
     * for `placement` passed to floating-ui.
     *
     * @see https://floating-ui.com/docs/tutorial#placements
     *
     * @default 'bottom'
     */
    placement?: Placement /**
     * The positioning strategy of the popover. If your reference element is in a fixed container
     * use the fixed strategy; otherwise use the default, absolute strategy.
     *
     * @see https://floating-ui.com/docs/computeposition#strategy
     *
     * @default 'absolute'
     */
    strategy?: Strategy
    /**
     * The label of the popover content. Must be provided if `labelledBy` is empty.
     *
     * @default undefined
     */
    label?: string
    /**
     * The id of the element labelling the popover content. Must be provided if `label` is empty.
     *
     * @default undefined
     */
    labelledBy?: string
    /**
     * the z-index to apply to the popover content
     */
    zIndex?: number | string
    /**
     * Whether the popover height should be clipped and made scrollable
     * if the window height is too small.
     *
     * @default false
     */
    clippable?: boolean
    /**
     * Whether the popover should trap focus. This means that when the popover is open,
     * the user cannot tab out of the popover content. This is useful for ensuring that
     * the popover content is accessible.
     * @default true
     */
    trapFocus?: boolean
  }>(),
  {
    activateOnHover: undefined,
    hideOnEsc: undefined,
    hideOnClickOutside: undefined,
    autoFocusOnShow: undefined,
    autoFocusOnHide: undefined,
    zIndex: "popover",
    clippable: false,
    trapFocus: undefined,
  }
)

if (!zIndexValidator(props.zIndex)) {
  throw new Error(`Invalid z-index value in VPopover: ${props.zIndex}`)
}

const emit = defineEmits<{
  /**
   * Fires when the popover opens, regardless of reason. There are no extra parameters.
   */
  open: []
  /**
   * Fires when the popover closes, regardless of reason. There are no extra parameters.
   */
  close: []
}>()

const visibleRef = ref(false)
const triggerContainerRef = ref<HTMLElement | null>(null)

const triggerRef = computed(() =>
  triggerContainerRef.value?.firstElementChild
    ? (triggerContainerRef.value.firstElementChild as HTMLElement)
    : undefined
)

const { close, onTriggerClick, triggerA11yProps } = useDialogControl({
  visibleRef,
  emit: emit as SetupContext["emit"],
})

defineExpose({
  close,
})
</script>

<template>
  <div>
    <!-- re: disabled static element interactions rule https://github.com/WordPress/openverse/issues/2906 -->
    <!-- eslint-disable-next-line vuejs-accessibility/click-events-have-key-events, vuejs-accessibility/no-static-element-interactions -->
    <div
      ref="triggerContainerRef"
      class="flex w-min items-stretch whitespace-nowrap"
      @click="onTriggerClick"
    >
      <!--
        @slot The trigger, should be a button 99.99% of the time. If you need custom event handling on the trigger button, ensure bubbling is not prevented or else the popover will not open
          @binding {object} a11yProps
          @binding {boolean} visible
      -->
      <slot
        name="trigger"
        :a11y-props="triggerA11yProps"
        :visible="visibleRef"
      />
    </div>
    <VPopoverContent
      v-if="triggerRef"
      :z-index="zIndex"
      :visible="visibleRef"
      :trigger-element="triggerRef"
      :placement="placement"
      :strategy="strategy"
      :clippable="clippable"
      :hide-on-esc="hideOnEsc"
      :hide-on-click-outside="hideOnClickOutside"
      :auto-focus-on-show="autoFocusOnShow"
      :auto-focus-on-hide="autoFocusOnHide"
      :trap-focus="trapFocus"
      :hide="close"
      :aria-label="label"
      :aria-labelledby="labelledBy"
    >
      <!--
        @slot The content of the popover
          @binding {function} close
      -->
      <slot name="default" :close="close" />
    </VPopoverContent>
  </div>
</template>
