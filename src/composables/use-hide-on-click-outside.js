import { ref, watch, computed } from '@nuxtjs/composition-api'

import { getDocument } from '~/utils/dom/get-document'

import { useEventListenerOutside } from './use-event-listener-outside'

/**
 * @typedef Props
 * @property {import('./types').Ref<HTMLElement>} dialogRef
 * @property {import('./types').Ref<boolean>} visibleRef
 * @property {import('./types').Ref<boolean>} hideOnClickOutsideRef
 * @property {import('./types').Ref<HTMLElement>} triggerElementRef
 * @property {import('./types').Ref<() => void>} hideRef
 */

/**
 * @param {Props} props
 * @return {import('./types').Ref<EventTarget>}
 */
function useMouseDownTargetRef({
  dialogRef,
  visibleRef,
  hideOnClickOutsideRef,
}) {
  const mouseDownTargetRef = ref()

  watch(
    [visibleRef, hideOnClickOutsideRef, dialogRef],
    /**
     * @param {[boolean, boolean, HTMLElement]} deps
     * @param {unknown} _
     * @param {(cb: () => void) => void} onInvalidate
     */
    ([visible, hideOnClickOutside, popover], _, onInvalidate) => {
      if (!(visible && hideOnClickOutside)) return

      const document = getDocument(popover)
      const onMouseDown = (event) => (mouseDownTargetRef.value = event.target)
      document.addEventListener('mousedown', onMouseDown)
      onInvalidate(() => {
        document.addEventListener('mousedown', onMouseDown)
      })
    },
    { immediate: true }
  )

  return mouseDownTargetRef
}

/**
 * @param {Props} props
 */
export function useHideOnClickOutside({
  dialogRef,
  visibleRef,
  hideOnClickOutsideRef,
  triggerElementRef,
  hideRef,
}) {
  const mouseDownTargetRef = useMouseDownTargetRef({
    dialogRef,
    visibleRef,
    hideOnClickOutsideRef,
  })

  const shouldListenRef = computed(
    () => visibleRef.value && hideOnClickOutsideRef.value
  )

  useEventListenerOutside({
    containerRef: dialogRef,
    triggerRef: triggerElementRef,
    eventType: 'click',
    listener: (event) => {
      if (mouseDownTargetRef.value === event.target) {
        // Make sure the element that has been clicked is the same that last
        // triggered the mousedown event. This prevents the dialog from closing
        // by dragging the cursor (for example, selecting some text inside the
        // dialog and releasing the mouse outside of it).
        hideRef.value()
      }
    },
    shouldListenRef,
  })

  useEventListenerOutside({
    containerRef: dialogRef,
    triggerRef: triggerElementRef,
    eventType: 'focusin',
    listener: (event) => {
      const document = getDocument(dialogRef.value)
      if (event.target !== document) {
        hideRef.value()
      }
    },
    shouldListenRef,
  })
}
