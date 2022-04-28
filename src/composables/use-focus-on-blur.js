import { getActiveElement } from 'reakit-utils/getActiveElement'
import { getNextActiveElementOnBlur } from 'reakit-utils/getNextActiveElementOnBlur'
import { ref, watch } from '@nuxtjs/composition-api'

import { getDocument } from '~/utils/dom/get-document'

/**
 * @typedef Props
 * @property {import('./types').Ref<HTMLElement>} dialogRef
 * @property {import('./types').Ref<boolean>} visibleRef
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
export function useFocusOnBlur({ dialogRef, visibleRef }) {
  const [blurredRef, scheduleFocus] = useBlurTracker()

  watch([blurredRef], ([blurred]) => {
    if (!visibleRef.value) return
    if (!blurred) return
    if (!isActualElement(getActiveElement(dialogRef.value))) {
      dialogRef.value?.focus()
    }
  })

  /**
   * @param {FocusEvent} event
   */
  const onBlur = (event) => {
    if (visibleRef.value) return
    const nextActiveElement = getNextActiveElementOnBlur(event)
    if (!isActualElement(nextActiveElement)) {
      scheduleFocus()
    }
  }

  return onBlur
}
