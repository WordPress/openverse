import { ref } from '@nuxtjs/composition-api'

import { PopoverContentProps, usePopper } from '~/composables/use-popper'

import { useDialogContent } from '~/composables/use-dialog-content'

import type { SetupContext } from 'vue'
import type { Ref, ToRefs } from '@nuxtjs/composition-api'

type Props = {
  popoverRef: Ref<HTMLElement | null>
  popoverPropsRefs: ToRefs<PopoverContentProps>
  emit: SetupContext['emit']
}

export function usePopoverContent({
  popoverRef,
  popoverPropsRefs,
  emit,
}: Props) {
  const { onKeyDown, onBlur } = useDialogContent({
    dialogRef: popoverRef,
    visibleRef: popoverPropsRefs.visible,
    autoFocusOnShowRef: popoverPropsRefs.autoFocusOnShow,
    autoFocusOnHideRef: popoverPropsRefs.autoFocusOnHide,
    trapFocusRef: ref(false),
    triggerElementRef: popoverPropsRefs.triggerElement,
    hideOnClickOutsideRef: popoverPropsRefs.hideOnClickOutside,
    hideRef: popoverPropsRefs.hide,
    hideOnEscRef: popoverPropsRefs.hideOnEsc,
    emit,
  })

  const { maxHeightRef } = usePopper({
    popoverRef,
    popoverPropsRefs,
  })

  return { onKeyDown, onBlur, maxHeightRef }
}
