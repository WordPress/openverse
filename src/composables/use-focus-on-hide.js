import { watch } from '@vue/composition-api'
import {
  isTabbable,
  getActiveElement,
  contains,
  ensureFocus,
} from 'reakit-utils'

/**
 * @typedef Props
 * @property {import('./types').Ref<HTMLElement>} popoverRef
 * @property {import('./types').ToRefs<import('../components/VPopover/VPopover.types').Props>} popoverPropsRefs
 */

/**
 * @param {HTMLElement} popover
 */
function hidByFocusingAnotherElement(popover) {
  if (!popover) return false

  const activeElement = getActiveElement(popover)

  if (!activeElement) return false
  if (contains(popover, activeElement)) return false
  if (isTabbable(activeElement)) return true

  return activeElement.getAttribute('data-popover') === 'true'
}

/**
 * @param {Props} Props
 */
export const useFocusOnHide = ({ popoverRef, popoverPropsRefs }) => {
  watch(
    [
      popoverRef,
      popoverPropsRefs.triggerElement,
      popoverPropsRefs.visible,
      popoverPropsRefs.autoFocusOnHide,
    ],
    /**
     * @param {[HTMLElement, HTMLElement, boolean, boolean]} deps
     * @param {[unknown, unknown, boolean]} previousDeps
     */
    (
      [popover, triggerElement, visible, autoFocusOnHide],
      [, , previousVisible]
    ) => {
      const shouldFocus =
        autoFocusOnHide && !visible && visible !== previousVisible

      if (!shouldFocus) return

      if (hidByFocusingAnotherElement(popover)) return

      ensureFocus(triggerElement)
    }
  )
}
