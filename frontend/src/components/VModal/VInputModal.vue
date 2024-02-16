<template>
  <div ref="nodeRef">
    <div v-if="!isActive" class="flex w-full"><slot /></div>
    <VTeleport v-else to="modal">
      <div
        class="fixed inset-0 z-40 flex h-[100dvh] h-screen w-full justify-center overflow-y-auto bg-white"
      >
        <!-- re: disabled static element interactions rule https://github.com/WordPress/openverse/issues/2906 -->
        <!-- eslint-disable-next-line vuejs-accessibility/no-static-element-interactions -->
        <div
          ref="dialogRef"
          v-bind="$attrs"
          class="flex w-full flex-col px-3 py-4"
          role="dialog"
          aria-modal="true"
          @keydown="onKeyDown"
          @blur="onBlur"
        >
          <slot />
        </div>
      </div>
    </VTeleport>
  </div>
</template>

<script lang="ts">
import {
  defineComponent,
  ref,
  toRef,
  ComponentInstance,
  SetupContext,
} from "vue"

import { Portal as VTeleport } from "portal-vue"

import { useDialogContent } from "~/composables/use-dialog-content"
import { useDialogControl } from "~/composables/use-dialog-control"

export default defineComponent({
  name: "VInputModal",
  components: { VTeleport },

  /**
   * NB: Most of these technically default to `undefined` so that the underlying `VPopoverContent`
   * default for each of them can take over.
   */
  props: {
    /**
     * This props allows for the modal to be opened or closed programmatically.
     * The modal handles the visibility internally if this prop is not provided.
     *
     * @default undefined
     */
    isActive: {
      type: Boolean,
      default: false,
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
  setup(props, { attrs, emit }) {
    const focusTrapRef = ref<ComponentInstance | null>(null)
    const nodeRef = ref<HTMLElement | null>(null)
    const dialogRef = ref<HTMLElement | null>(null)

    const visibleRef = toRef(props, "isActive")

    const deactivateRef = ref()

    const { close } = useDialogControl({
      visibleRef,
      nodeRef,
      emit: emit as SetupContext["emit"],
      deactivateFocusTrap: deactivateRef,
    })

    const { onKeyDown, onBlur, deactivateFocusTrap } = useDialogContent({
      dialogElements: {
        dialogRef,
        triggerElementRef: ref(null),
        initialFocusElementRef: ref(null),
      },
      dialogOptions: {
        autoFocusOnHideRef: ref(false),
        hideOnClickOutsideRef: ref(false),
        hideOnEscRef: ref(true),
        trapFocusRef: ref(true),
      },
      visibleRef: toRef(props, "isActive"),
      hideRef: ref(close),
      emit: emit as SetupContext["emit"],
      attrs,
    })
    deactivateRef.value = deactivateFocusTrap

    return {
      focusTrapRef,
      dialogRef,
      nodeRef,
      visibleRef,

      close,
      onKeyDown,
      onBlur,
    }
  },
})
</script>
