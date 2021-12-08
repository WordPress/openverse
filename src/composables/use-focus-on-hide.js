import { watch } from '@vue/composition-api'
import {
  isTabbable,
  getActiveElement,
  contains,
  ensureFocus,
} from 'reakit-utils'

/**
 * @typedef Props
 * @property {import('./types').Ref<HTMLElement>} dialogRef
 * @property {import('./types').Ref<HTMLElement>} triggerElementRef
 * @property {import('./types').Ref<boolean>} visibleRef
 * @property {import('./types').Ref<boolean>} autoFocusOnHideRef
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
export const useFocusOnHide = ({
  dialogRef,
  triggerElementRef,
  visibleRef,
  autoFocusOnHideRef,
}) => {
  watch(
    [dialogRef, triggerElementRef, visibleRef, autoFocusOnHideRef],
    /**
     * @param {[HTMLElement, HTMLElement, boolean, boolean]} deps
     * @param {[unknown, unknown, boolean]} previousDeps
     */
    (
      [dialog, triggerElement, visible, autoFocusOnHide],
      [, , previousVisible]
    ) => {
      const shouldFocus =
        autoFocusOnHide && !visible && visible !== previousVisible

      if (!shouldFocus) return

      if (hidByFocusingAnotherElement(dialog)) return

      ensureFocus(triggerElement)
    }
  )
}
