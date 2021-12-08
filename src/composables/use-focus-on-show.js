import { watch } from '@nuxtjs/composition-api'
import { getFirstTabbableIn, hasFocusWithin, ensureFocus } from 'reakit-utils'
import { warn } from '~/utils/warn'

export const noFocusableElementWarning =
  "It's recommended to have at least one tabbable element inside dialog. The dialog element has been automatically focused. If this is the intended behavior, pass `tabIndex={0}` to the dialog element to disable this warning."

/**
 * @typedef Props
 * @property {import('./types').Ref<HTMLElement>} dialogRef
 * @property {import('./types').Ref<boolean>} visibleRef
 * @property {import('./types').Ref<boolean>} autoFocusOnShowRef
 */

/**
 * @see https://github.com/reakit/reakit/blob/bce9b8a0e567983f61b5cc627f8dee9461986fab/packages/reakit/src/Dialog/__utils/useFocusOnShow.ts#L9
 * @param {Props} props
 */
export const useFocusOnShow = ({
  dialogRef,
  visibleRef,
  autoFocusOnShowRef,
}) => {
  watch(
    [dialogRef, visibleRef, autoFocusOnShowRef],
    /**
     * @param {[HTMLElement, boolean, boolean]} values
     */
    ([dialog, visible, autoFocusOnShow]) => {
      if (!dialog || !visible || !autoFocusOnShow) return

      const tabbable = getFirstTabbableIn(dialog, true)
      const isActive = () => hasFocusWithin(dialog)

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
