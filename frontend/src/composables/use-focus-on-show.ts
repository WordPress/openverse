import { nextTick, watch, Ref, computed, ref } from "vue"

import { tryOnScopeDispose, unrefElement } from "@vueuse/core"

import { warn } from "~/utils/console"
import {
  ensureFocus,
  getFirstTabbableIn,
  hasFocusWithin,
} from "~/utils/reakit-utils/focus"
import { useFocusTrap, UseFocusTrapReturn } from "~/composables/use-focus-trap"

export const noFocusableElementWarning =
  "It's recommended to have at least one tabbable element inside dialog. The dialog element has been automatically focused. If this is the intended behavior, pass `tabIndex={0}` to the dialog element to disable this warning."

type Props = {
  dialogRef: Ref<HTMLElement | null>
  visibleRef: Ref<boolean>
  autoFocusOnShowRef: Ref<boolean>
  trapFocusRef: Ref<boolean>
  hideOnClickOutsideRef: Ref<boolean>
  initialFocusElementRef: Ref<HTMLElement | null>
}

/**
 * @see https://github.com/reakit/reakit/blob/bce9b8a0e567983f61b5cc627f8dee9461986fab/packages/reakit/src/Dialog/__utils/useFocusOnShow.ts#L9
 */
export const useFocusOnShow = ({
  dialogRef,
  visibleRef,
  autoFocusOnShowRef,
  trapFocusRef,
  hideOnClickOutsideRef,
  initialFocusElementRef,
}: Props) => {
  let activateFocusTrap = () => {
    /** */
  }
  let deactivateFocusTrap = () => {
    /** */
  }
  let trap: UseFocusTrapReturn | undefined
  const foundTabbableNode = ref<HTMLElement | null>(null)
  const fallbackFocusNode = computed(
    () => initialFocusElementRef.value || foundTabbableNode.value
  )
  if (trapFocusRef.value) {
    trap = useFocusTrap(dialogRef, {
      // Prevent FocusTrap from trying to focus the first element.
      // We already do that in a more flexible, adaptive way in our Dialog composables.
      initialFocus: false,
      // if set to true, focus-trap prevents the default for the keyboard event, and we cannot handle it in our composables.
      escapeDeactivates: false,
      clickOutsideDeactivates: () => hideOnClickOutsideRef.value,
      // Even though we pass `initialFocus` as `false` above, `focus-trap` still
      // checks if the container has at least one tabbable element. Because it sometimes
      // doesn't play nicely with Vue's rendering life-cycle, we need to get it a
      // dynamic way to retrieve the fallback node.
      fallbackFocus: () => fallbackFocusNode.value as HTMLElement,
    })

    activateFocusTrap = trap.activate
    deactivateFocusTrap = trap.deactivate
  }

  const stopWatcher = watch(
    [
      () => unrefElement(dialogRef),
      visibleRef,
      autoFocusOnShowRef,
      initialFocusElementRef,
    ] as const,
    ([dialog, visible, autoFocusOnShow, initialFocusElement], _, onCleanup) => {
      if (!dialog || !visible) {
        if (trap?.hasFocus) {deactivateFocusTrap()}
        return
      }
      if (!autoFocusOnShow) {return}

      nextTick(() => {
        const isActive = () => hasFocusWithin(dialog)

        if (initialFocusElement) {
          ensureFocus(initialFocusElement, {
            preventScroll: true,
            isActive,
          })
        } else {
          const tabbable = getFirstTabbableIn(dialog, true)

          if (tabbable) {
            ensureFocus(tabbable, { preventScroll: true, isActive })
            foundTabbableNode.value = tabbable
          } else {
            ensureFocus(dialog, { preventScroll: true, isActive })
            foundTabbableNode.value = dialog
            if (dialog.tabIndex === undefined || dialog.tabIndex < 0) {
              warn(noFocusableElementWarning)
            }
          }
        }
        activateFocusTrap()
      })

      onCleanup(() => {
        deactivateFocusTrap()
      })
    }
  )
  tryOnScopeDispose(() => {
    deactivateFocusTrap()
    stopWatcher()
  })
  return { deactivateFocusTrap }
}
