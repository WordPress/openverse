<template>
  <div ref="nodeRef">
    <!-- re: disabled static element interactions rule https://github.com/WordPress/openverse/issues/2906 -->
    <!-- eslint-disable-next-line vuejs-accessibility/click-events-have-key-events, vuejs-accessibility/no-static-element-interactions -->
    <div ref="triggerContainerRef" class="flex" @click="onTriggerClick">
      <!--
        @slot The trigger. Should be a button 99% of the time. If you need custom event handling on the trigger button, ensure bubbling is not prevented or else the dialog will not open.
          @binding {object} a11yProps Props to v-bind to the trigger element to ensure accessibility
          @binding {boolean} visible Whether the dialog is currently visible (open)
      -->
      <slot
        name="trigger"
        :a11y-props="triggerA11yProps"
        :visible="visibleRef"
      />
    </div>
    <VModalContent
      v-if="triggerRef"
      ref="modalContentRef"
      :visible="visibleRef"
      :trigger-element="triggerRef"
      :hide-on-esc="hideOnEsc"
      :hide-on-click-outside="hideOnClickOutside"
      :auto-focus-on-show="autoFocusOnShow"
      :auto-focus-on-hide="autoFocusOnHide"
      :hide="close"
      :aria-label="label"
      :aria-labelledby="labelledBy"
      :initial-focus-element="initialFocusElement"
      :variant="variant"
      :mode="mode"
      :content-classes="modalContentClasses"
    >
      <template #top-bar="{ close: hide }">
        <slot name="top-bar" :close="hide" />
      </template>
      <slot name="default" />
    </VModalContent>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, PropType, SetupContext } from "vue"

import type { ModalColorMode, ModalVariant } from "~/types/modal"

import { useDialogControl } from "~/composables/use-dialog-control"

import VModalContent from "~/components/VModal/VModalContent.vue"

export default defineComponent({
  name: "VModal",
  components: { VModalContent },
  /**
   * NB: Most of these technically default to `undefined` so that the underlying `VPopoverContent`
   * default for each of them can take over.
   */
  props: {
    /**
     * Whether the popover should hide when the <kbd>Escape</kbd> key is pressed.
     *
     * @default true
     */
    hideOnEsc: { type: Boolean, default: undefined },
    /**
     * Whether the popover should hide when a click happens outside the popover content,
     * excluding the trigger. When the trigger is clicked and the popover is open, nothing
     * will happen.
     *
     * @default true
     */
    hideOnClickOutside: { type: Boolean, default: undefined },
    /**
     * Whether the popover content should automatically receive focus when the popover
     * opens.
     *
     * @default true
     */
    autoFocusOnShow: { type: Boolean, default: undefined },
    /**
     * Whether the trigger should automatically receive focus when the popover closes.
     *
     * @default true
     */
    autoFocusOnHide: { type: Boolean, default: undefined },
    /**
     * The label of the popover content. Must be provided if `labelledBy` is empty.
     *
     * @default undefined
     */
    label: { type: String },
    /**
     * The id of the element labelling the popover content. Must be provided if `label` is empty.
     *
     * @default undefined
     */
    labelledBy: { type: String },
    /**
     * The element to focus when the modal is opened. If nothing is
     * passed, then the first tabbable element in the modal content
     * will be focused. If no tabbable element is found in the modal
     * content, then the entire modal content itself will be focused.
     *
     * @default undefined
     */
    initialFocusElement: {
      type: (import.meta.server
        ? Object
        : HTMLElement) as PropType<HTMLElement>,
      default: undefined,
    },
    /**
     * The variant of the modal content.
     * The `default` variant is a full-screen modal on mobile widths, and is a smaller mobile
     * on a grayed out backdrop on larger screens.
     *
     * The `full` variant is a full-screen modal on all screen widths. It is currently
     * only used for mobile version of the `VHeaderInternal` component.
     *
     * @default 'default'
     */
    variant: {
      type: String as PropType<ModalVariant>,
      default: "default",
    },
    /**
     * The color mode of the modal content.
     * The default `light` mode uses dark charcoal content on the white background.
     * The `dark` mode uses white content on the dark charcoal background.
     *
     * @default 'light'
     */
    mode: {
      type: String as PropType<ModalColorMode>,
      default: "light",
    },
    modalContentClasses: {
      type: String,
      default: "",
    },
  },
  emits: [
    /**
     * Fires when the popover opens, regardless of reason. There are no extra parameters.
     */
    "open",
    /**
     * Fires when the popover closes, regardless of reason. There are no extra parameters.
     */
    "close",
  ],
  setup(_, { emit }) {
    const nodeRef = ref<null | HTMLElement>(null)
    const modalContentRef = ref<InstanceType<typeof VModalContent> | null>(null)
    const triggerContainerRef = ref<HTMLElement | null>(null)

    const triggerRef = computed(
      () =>
        triggerContainerRef.value?.firstElementChild as HTMLElement | undefined
    )

    const deactivateFocusTrap = computed(
      () => modalContentRef.value?.deactivateFocusTrap
    )

    const {
      close,
      open,
      onTriggerClick,
      triggerA11yProps,
      visible: visibleRef,
    } = useDialogControl({
      lockBodyScroll: true,
      nodeRef,
      emit: emit as SetupContext["emit"],
      deactivateFocusTrap,
    })

    return {
      nodeRef,
      modalContentRef,
      visibleRef,
      triggerContainerRef,
      triggerRef,

      close,
      open,
      onTriggerClick,
      triggerA11yProps,
      deactivateFocusTrap,
    }
  },
})
</script>
