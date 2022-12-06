import { nextTick, ref, watch, Ref } from '@nuxtjs/composition-api'

import { warn } from '~/utils/console'
import {
  ensureFocus,
  getFirstTabbableIn,
  hasFocusWithin,
} from '~/utils/reakit-utils/focus'
import { useFocusTrap } from '~/composables/use-focus-trap'

export const noFocusableElementWarning =
  "It's recommended to have at least one tabbable element inside dialog. The dialog element has been automatically focused. If this is the intended behavior, pass `tabIndex={0}` to the dialog element to disable this warning."

type Props = {
  dialogRef: Ref<HTMLElement | null>
  visibleRef: Ref<boolean>
  autoFocusOnShowRef: Ref<boolean>
  initialFocusElementRef?: Ref<HTMLElement | null>
}

/**
 * @see https://github.com/reakit/reakit/blob/bce9b8a0e567983f61b5cc627f8dee9461986fab/packages/reakit/src/Dialog/__utils/useFocusOnShow.ts#L9
 */
export const useFocusOnShow = ({
  dialogRef,
  visibleRef,
  autoFocusOnShowRef,
  initialFocusElementRef = ref(null),
}: Props) => {
  const { activate: activateFocusTrap, deactivate: deactivateFocusTrap } =
    useFocusTrap(dialogRef, {
      // Prevent FocusTrap from trying to focus the first element.
      // We already do that in a more flexible, adaptive way in our Dialog composables.
      initialFocus: false,
      // if set to true, focus-trap prevents the default for the keyboard event, and we cannot handle it in our composables.
      escapeDeactivates: false,
    })

  watch(
    [
      dialogRef,
      visibleRef,
      autoFocusOnShowRef,
      initialFocusElementRef,
    ] as const,
    ([dialog, visible, autoFocusOnShow, initialFocusElement]) => {
      if (!dialog || !visible) {
        deactivateFocusTrap()
        return
      }
      if (!dialog || !visible || !autoFocusOnShow) return

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
          } else {
            ensureFocus(dialog, { preventScroll: true, isActive })
            if (dialog.tabIndex === undefined || dialog.tabIndex < 0) {
              warn(noFocusableElementWarning)
            }
          }
        }
        activateFocusTrap()
      })
    }
  )
}
