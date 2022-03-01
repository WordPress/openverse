import { ref, watch } from '@nuxtjs/composition-api'
import { getFirstTabbableIn } from 'reakit-utils/tabbable'
import { hasFocusWithin } from 'reakit-utils/hasFocusWithin'
import { ensureFocus } from 'reakit-utils/ensureFocus'

import { warn } from '~/utils/console'

export const noFocusableElementWarning =
  "It's recommended to have at least one tabbable element inside dialog. The dialog element has been automatically focused. If this is the intended behavior, pass `tabIndex={0}` to the dialog element to disable this warning."

/**
 * @typedef Props
 * @property {import('./types').Ref<HTMLElement>} dialogRef
 * @property {import('./types').Ref<boolean>} visibleRef
 * @property {import('./types').Ref<boolean>} autoFocusOnShowRef
 * @property {import('./types').Ref<HTMLElement>} initialFocusElementRef
 */

/**
 * @see https://github.com/reakit/reakit/blob/bce9b8a0e567983f61b5cc627f8dee9461986fab/packages/reakit/src/Dialog/__utils/useFocusOnShow.ts#L9
 * @param {Props} props
 */
export const useFocusOnShow = ({
  dialogRef,
  visibleRef,
  autoFocusOnShowRef,
  initialFocusElementRef = ref(),
}) => {
  watch(
    [dialogRef, visibleRef, autoFocusOnShowRef, initialFocusElementRef],
    /**
     * @param {[HTMLElement, boolean, boolean, HTMLElement]} values
     */
    ([dialog, visible, autoFocusOnShow, initialFocusElement]) => {
      if (!dialog || !visible || !autoFocusOnShow) return

      const isActive = () => hasFocusWithin(dialog)

      if (initialFocusElement) {
        return ensureFocus(initialFocusElement, {
          preventScroll: true,
          isActive,
        })
      }

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
  )
}
