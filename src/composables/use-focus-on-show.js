import { watch } from '@nuxtjs/composition-api'
import { getFirstTabbableIn, hasFocusWithin, ensureFocus } from 'reakit-utils'
import { warn } from '~/utils/warn'

export const noFocusableElementWarning =
  "It's recommended to have at least one tabbable element inside dialog. The dialog element has been automatically focused. If this is the intended behavior, pass `tabIndex={0}` to the dialog element to disable this warning."

/**
 * @typedef Props
 * @property {import('./types').Ref<HTMLElement>} popoverRef
 * @property {import('./types').ToRefs<import('../components/VPopover/VPopover.types').Props>} popoverPropsRefs
 */

/**
 * @see https://github.com/reakit/reakit/blob/bce9b8a0e567983f61b5cc627f8dee9461986fab/packages/reakit/src/Dialog/__utils/useFocusOnShow.ts#L9
 * @param {Props} props
 */
export const useFocusOnShow = ({ popoverRef, popoverPropsRefs }) => {
  watch(
    [popoverRef, popoverPropsRefs.visible, popoverPropsRefs.autoFocusOnShow],
    /**
     * @param {[HTMLElement, boolean, boolean]} values
     */
    ([popover, visible, autoFocusOnShow]) => {
      if (!popover || !visible || !autoFocusOnShow) return

      const tabbable = getFirstTabbableIn(popover, true)
      const isActive = () => hasFocusWithin(popover)

      if (tabbable) {
        ensureFocus(tabbable, { preventScroll: true, isActive })
      } else {
        ensureFocus(popover, { preventScroll: true, isActive })
        if (popover.tabIndex === undefined || popover.tabIndex < 0) {
          warn(noFocusableElementWarning)
        }
      }
    }
  )
}
