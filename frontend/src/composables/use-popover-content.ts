import { computed, ref } from "vue"

import { PopoverContentProps, usePopper } from "~/composables/use-popper"

import { useDialogContent } from "~/composables/use-dialog-content"

import type { CSSProperties } from "@vue/runtime-dom"

import type { Ref, ToRefs, SetupContext } from "vue"

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
      trapFocusRef: ref(false),
    },
    emit,
    attrs,
  })

  const { maxHeightRef } = usePopper({
    popoverRef,
    popoverPropsRefs,
  })

  const heightProperties = computed(() => {
    // extracting this to ensure that computed is updated when the value changes
    const maxHeight = maxHeightRef.value

    return maxHeight && popoverPropsRefs.clippable
      ? ({ "--popover-height": `${maxHeight}px` } as CSSProperties)
      : ({} as CSSProperties)
  })

  return { onKeyDown, onBlur, heightProperties }
}
