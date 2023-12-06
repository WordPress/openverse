import { Ref, ref, watch } from "vue"

import { getActiveElement, getDocument } from "~/utils/reakit-utils/dom"

type Props = {
  dialogRef: Ref<HTMLElement | null>
  visibleRef: Ref<boolean>
}

function isActualElement(
  element: EventTarget | Element | null
): element is Element {
  if (!element) {return false}
  const elementAsElement = element as Element
  return !!(
    elementAsElement.tagName &&
    elementAsElement.tagName !== "HTML" &&
    elementAsElement !== getDocument(elementAsElement).body
  )
}

function useBlurTracker(): [Ref<number>, () => void] {
  const blurredRef = ref(0)

  const scheduleFocus = () => (blurredRef.value += 1)

  return [blurredRef, scheduleFocus]
}

export function useFocusOnBlur({ dialogRef, visibleRef }: Props) {
  const [blurredRef, scheduleFocus] = useBlurTracker()

  watch([blurredRef], ([blurred]) => {
    if (!visibleRef.value) {return}
    if (!blurred) {return}
    if (!isActualElement(getActiveElement(dialogRef.value))) {
      dialogRef.value?.focus()
    }
  })

  return (event: FocusEvent) => {
    if (visibleRef.value) {return}
    const nextActiveElement = event.relatedTarget
    if (!isActualElement(nextActiveElement as Element)) {
      scheduleFocus()
    }
  }
}
