import { Ref, watch } from "vue"

import { contains, getActiveElement } from "~/utils/reakit-utils/dom"
import { ensureFocus, isTabbable } from "~/utils/reakit-utils/focus"

type Props = {
  dialogRef: Ref<HTMLElement | null>
  triggerElementRef: Ref<HTMLElement | null>
  visibleRef: Ref<boolean>
  autoFocusOnHideRef: Ref<boolean>
}

function hidByFocusingAnotherElement(popover: HTMLElement) {
  if (!popover) {
    return false
  }

  const activeElement = getActiveElement(popover)

  if (!activeElement) {
    return false
  }
  if (contains(popover, activeElement)) {
    return false
  }
  if (isTabbable(activeElement)) {
    return true
  }

  return activeElement.getAttribute("data-popover") === "true"
}

export const useFocusOnHide = ({
  dialogRef,
  triggerElementRef,
  visibleRef,
  autoFocusOnHideRef,
}: Props) => {
  watch(
    [dialogRef, triggerElementRef, visibleRef, autoFocusOnHideRef] as const,

    (
      [dialog, triggerElement, visible, autoFocusOnHide],
      [, , previousVisible]
    ) => {
      const shouldFocus =
        autoFocusOnHide && !visible && visible !== previousVisible

      if (!shouldFocus) {
        return
      }

      if (!dialog || hidByFocusingAnotherElement(dialog)) {
        return
      }

      if (triggerElement) {
        ensureFocus(triggerElement)
      }
    }
  )
}
