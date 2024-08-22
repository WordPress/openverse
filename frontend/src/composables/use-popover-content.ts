import { computed, ref } from "vue"

import { useFloatingUi } from "~/composables/use-floating-ui"

import { useDialogContent } from "~/composables/use-dialog-content"

import type { Properties as CSSProperties } from "csstype"

import type { Ref, ToRefs, SetupContext } from "vue"
import type { Placement, Strategy } from "@floating-ui/dom"

export type PopoverContentProps = {
  id: string
  visible: boolean
  hide: () => void
  hideOnEsc: boolean
  hideOnClickOutside: boolean
  autoFocusOnShow: boolean
  autoFocusOnHide: boolean
  triggerElement: HTMLElement | null
  placement: Placement
  strategy: Strategy
  clippable: boolean
  trapFocus: boolean
  zIndex: number | string
}
type Props = {
  popoverRef: Ref<HTMLElement | null>
  popoverPropsRefs: ToRefs<PopoverContentProps>
  emit: SetupContext["emit"]
  attrs: SetupContext["attrs"]
}

export function usePopoverContent({
  popoverRef,
  popoverPropsRefs,
  emit,
  attrs,
}: Props) {
  const { onKeyDown, onBlur } = useDialogContent({
    id: popoverPropsRefs.id,
    visibleRef: popoverPropsRefs.visible,
    hideRef: popoverPropsRefs.hide,
    dialogElements: {
      dialogRef: popoverRef,
      triggerElementRef: popoverPropsRefs.triggerElement,
      initialFocusElementRef: ref(null),
    },
    dialogOptions: {
      autoFocusOnShowRef: popoverPropsRefs.autoFocusOnShow,
      autoFocusOnHideRef: popoverPropsRefs.autoFocusOnHide,
      hideOnClickOutsideRef: popoverPropsRefs.hideOnClickOutside,
      hideOnEscRef: popoverPropsRefs.hideOnEsc,
      trapFocusRef: popoverPropsRefs.trapFocus,
    },
    emit,
    attrs,
  })

  const { style, maxHeightRef } = useFloatingUi({
    floatingElRef: popoverRef,
    floatingPropsRefs: popoverPropsRefs,
  })

  const heightProperties = computed(() => {
    // extracting this to ensure that computed is updated when the value changes
    const maxHeight = maxHeightRef.value

    return maxHeight && popoverPropsRefs.clippable
      ? ({ "--popover-height": `${maxHeight}px` } as CSSProperties)
      : ({} as CSSProperties)
  })

  return { onKeyDown, onBlur, style, heightProperties }
}
