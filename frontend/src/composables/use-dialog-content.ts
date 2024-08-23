import { ref } from "vue"

import { useFocusOnShow } from "~/composables/use-focus-on-show"
import { useFocusOnHide } from "~/composables/use-focus-on-hide"
import { useHideOnClickOutside } from "~/composables/use-hide-on-click-outside"
import { useFocusOnBlur } from "~/composables/use-focus-on-blur"

import { warn } from "~/utils/console"

import type { DialogElements, DialogOptions } from "~/types/modal"

import type { Ref, SetupContext } from "vue"

type Props = {
  dialogElements: DialogElements
  dialogOptions?: Partial<DialogOptions>
  visibleRef: Ref<boolean>
  hideRef: Ref<() => void>
  emit: SetupContext["emit"]
  attrs: SetupContext["attrs"]
}

export function useDialogContent({
  emit,
  attrs,
  visibleRef,
  hideRef,
  dialogOptions,
  dialogElements: { dialogRef, initialFocusElementRef, triggerElementRef },
}: Props) {
  if (!attrs["aria-label"] && !attrs["aria-labelledby"]) {
    warn("You should provide either `aria-label` or `aria-labelledby` props.")
  }

  const autoFocusOnShowRef = dialogOptions?.autoFocusOnShowRef || ref(true)
  const trapFocusRef = dialogOptions?.trapFocusRef || ref(true)
  const autoFocusOnHideRef = dialogOptions?.autoFocusOnHideRef || ref(true)
  const hideOnClickOutsideRef =
    dialogOptions?.hideOnClickOutsideRef || ref(true)
  const hideOnEscRef = dialogOptions?.hideOnEscRef || ref(true)

  const focusOnBlur = useFocusOnBlur({
    dialogRef,
    visibleRef,
  })
  const { deactivateFocusTrap } = useFocusOnShow({
    dialogRef,
    visibleRef,
    initialFocusElementRef,

    autoFocusOnShowRef,
    trapFocusRef,
    hideOnClickOutsideRef,
  })
  useFocusOnHide({
    dialogRef,
    triggerElementRef,
    visibleRef,
    autoFocusOnHideRef,
  })
  useHideOnClickOutside({
    dialogRef,
    triggerElementRef,

    hideOnClickOutsideRef,
    hideRef,
    visibleRef,
  })

  const onKeyDown = (event: KeyboardEvent) => {
    emit("keydown", event)

    if (event.defaultPrevented) {
      return
    }
    if (event.key !== "Escape") {
      return
    }
    if (!hideOnEscRef.value) {
      return
    }

    event.stopPropagation()
    hideRef.value()
  }

  const onBlur = (event: FocusEvent) => {
    emit("blur", event)
    focusOnBlur(event)
  }

  return { onKeyDown, onBlur, deactivateFocusTrap }
}
