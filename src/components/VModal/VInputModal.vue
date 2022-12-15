<template>
  <div ref="nodeRef">
    <div v-if="!isActive" class="flex w-full"><slot /></div>
    <VTeleport v-else to="modal">
      <div
        class="fixed inset-0 z-40 flex min-h-screen w-full justify-center overflow-y-auto bg-white"
      >
        <div
          ref="dialogRef"
          v-bind="$attrs"
          class="flex w-full flex-col py-4 px-4"
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
  watch,
  toRef,
  ComponentInstance,
} from "@nuxtjs/composition-api"

import { Portal as VTeleport } from "portal-vue"

import { useBodyScrollLock } from "~/composables/use-body-scroll-lock"
import { useDialogContent } from "~/composables/use-dialog-content"

import type { SetupContext } from "vue"

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
  setup(props, { emit }) {
    const focusTrapRef = ref<ComponentInstance | null>(null)

    const visibleRef = toRef(props, "isActive")
    const internalVisibleRef = ref<boolean>(
      props.isActive === undefined ? false : visibleRef.value
    )

    const nodeRef = ref<HTMLElement | null>(null)

    /**
     * When the `visible` prop is set to a different value than internalVisibleRef,
     * we update the internalVisibleRef to match the prop.
     */
    watch(visibleRef, (visible) => {
      if (visible === undefined || visible === internalVisibleRef.value) return

      if (visible) {
        open()
      } else {
        close()
      }
    })

    const { lock, unlock } = useBodyScrollLock({ nodeRef })

    const open = () => {
      internalVisibleRef.value = true
      lock()
      if (props.isActive !== internalVisibleRef.value) {
        emit("open")
      }
    }

    const close = () => {
      internalVisibleRef.value = false
      unlock()
      emit("close")
    }

    const dialogRef = ref<HTMLElement | null>(null)

    const { onKeyDown, onBlur } = useDialogContent({
      dialogRef,
      visibleRef: toRef(props, "isActive"),
      autoFocusOnShowRef: ref(true),
      autoFocusOnHideRef: ref(false),
      triggerElementRef: ref(null),
      hideOnClickOutsideRef: ref(false),
      trapFocusRef: ref(true),
      hideRef: ref(close),
      hideOnEscRef: ref(true),
      emit: emit as SetupContext["emit"],
    })

    return {
      focusTrapRef,
      dialogRef,
      nodeRef,
      internalVisibleRef,

      close,
      onKeyDown,
      onBlur,
    }
  },
})
</script>
