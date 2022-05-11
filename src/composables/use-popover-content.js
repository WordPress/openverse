import { usePopper } from '~/composables/use-popper'

import { useDialogContent } from './use-dialog-content'

/**
 * @typedef Props
 * @property {import('./types').Ref<HTMLElement>} popoverRef
 * @property {import('./types').ToRefs<import('~/components/VPopover/VPopoverContent.types').Props>} popoverPropsRefs
 * @property {import('@nuxtjs/composition-api').SetupContext['emit']} emit
 */

/**
 * @param {Props} props
 */
export function usePopoverContent({ popoverRef, popoverPropsRefs, emit }) {
  const { onKeyDown, onBlur } = useDialogContent({
    dialogRef: popoverRef,
    visibleRef: popoverPropsRefs.visible,
    autoFocusOnShowRef: popoverPropsRefs.autoFocusOnShow,
    autoFocusOnHideRef: popoverPropsRefs.autoFocusOnHide,
    triggerElementRef: popoverPropsRefs.triggerElement,
    hideOnClickOutsideRef: popoverPropsRefs.hideOnClickOutside,
    hideRef: popoverPropsRefs.hide,
    hideOnEscRef: popoverPropsRefs.hideOnEsc,
    emit,
  })
  usePopper({
    popoverRef,
    popoverPropsRefs,
  })

  return { onKeyDown, onBlur }
}
