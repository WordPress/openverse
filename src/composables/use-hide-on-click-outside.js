import { ref, watch, computed } from '@nuxtjs/composition-api'
import { getDocument } from 'reakit-utils'
import { useEventListenerOutside } from './use-event-listener-outside'

/**
 * @typedef Props
 * @property {import('./types').Ref<HTMLElement>} popoverRef
 * @property {import('./types').ToRefs<import('../components/VPopover/VPopover.types').Props>} popoverPropsRefs
 */

/**
 * @param {Props} props
 * @return {import('./types').Ref<EventTarget>}
 */
function useMouseDownTargetRef({ popoverRef, popoverPropsRefs }) {
  const mouseDownTargetRef = ref()

  watch(
    [popoverPropsRefs.visible, popoverPropsRefs.hideOnClickOutside, popoverRef],
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
export function useHideOnClickOutside({ popoverRef, popoverPropsRefs }) {
  const mouseDownTargetRef = useMouseDownTargetRef({
    popoverRef,
    popoverPropsRefs,
  })

  const shouldListenRef = computed(
    () =>
      popoverPropsRefs.visible.value &&
      popoverPropsRefs.hideOnClickOutside.value
  )

  useEventListenerOutside({
    containerRef: popoverRef,
    triggerRef: popoverPropsRefs.triggerElement,
    eventType: 'click',
    listener: (event) => {
      if (mouseDownTargetRef.value === event.target) {
        // Make sure the element that has been clicked is the same that last
        // triggered the mousedown event. This prevents the dialog from closing
        // by dragging the cursor (for example, selecting some text inside the
        // dialog and releasing the mouse outside of it).
        popoverPropsRefs.hide.value()
      }
    },
    shouldListenRef,
  })

  useEventListenerOutside({
    containerRef: popoverRef,
    triggerRef: popoverPropsRefs.triggerElement,
    eventType: 'focusin',
    listener: (event) => {
      const document = getDocument(popoverRef.value)
      if (event.target !== document) {
        popoverPropsRefs.hide.value()
      }
    },
    shouldListenRef,
  })
}
