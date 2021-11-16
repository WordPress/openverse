import {
  getDocument,
  getActiveElement,
  getNextActiveElementOnBlur,
} from 'reakit-utils'
import { ref, watch } from '@nuxtjs/composition-api'

/**
 * @typedef Props
 * @property {import('./types').Ref<HTMLElement>} popoverRef
 * @property {import('./types').ToRefs<import('../components/VPopover/VPopover.types').Props>} popoverPropsRefs
 */

/**
 *
 * @param {Element | null} element
 * @return {element is Element}
 */
function isActualElement(element) {
  return (
    element &&
    element.tagName &&
    element.tagName !== 'HTML' &&
    element !== getDocument(element).body
  )
}

/**
 * @returns {[import('./types').Ref<number>, (n: number) => void]}
 */
function useBlurTracker() {
  const blurredRef = ref(0)

  const scheduleFocus = () => (blurredRef.value += 1)

  return [blurredRef, scheduleFocus]
}

/**
 * @param {Props} props
 */
export function useFocusOnBlur({ popoverRef, popoverPropsRefs }) {
  const [blurredRef, scheduleFocus] = useBlurTracker()

  watch([blurredRef], ([blurred]) => {
    if (!popoverPropsRefs.visible.value) return
    if (!blurred) return
    if (!isActualElement(getActiveElement(popoverRef.value))) {
      popoverRef.value?.focus()
    }
  })

  /**
   * @param {FocusEvent} event
   */
  const onBlur = (event) => {
    if (popoverPropsRefs.visible.value) return
    const nextActiveElement = getNextActiveElementOnBlur(event)
    if (!isActualElement(nextActiveElement)) {
      scheduleFocus()
    }
  }

  return onBlur
}
