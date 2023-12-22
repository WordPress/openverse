import { ref, watch, computed, Ref } from "vue"

import { getDocument } from "~/utils/reakit-utils/dom"
import { useEventListenerOutside } from "~/composables/use-event-listener-outside"

type Props = {
  dialogRef: Ref<HTMLElement | null>
  visibleRef: Ref<boolean>
  hideOnClickOutsideRef: Ref<boolean>
  triggerElementRef: Ref<HTMLElement | null>
  hideRef: Ref<() => void>
}

function useMouseDownTargetRef({
  dialogRef,
  visibleRef,
  hideOnClickOutsideRef,
}: {
  dialogRef: Props["dialogRef"]
  visibleRef: Props["visibleRef"]
  hideOnClickOutsideRef: Props["hideOnClickOutsideRef"]
}): Ref<EventTarget> {
  const mouseDownTargetRef = ref()

  watch(
    [visibleRef, hideOnClickOutsideRef, dialogRef] as const,
    ([visible, hideOnClickOutside, popover], _, onInvalidate) => {
      if (!(visible && hideOnClickOutside)) {
        return
      }

      const document = getDocument(popover)
      const onMouseDown = (event: MouseEvent) =>
        (mouseDownTargetRef.value = event.target)
      document.addEventListener("mousedown", onMouseDown)
      onInvalidate(() => {
        document.removeEventListener("mousedown", onMouseDown)
      })
    },
    { immediate: true }
  )

  return mouseDownTargetRef
}

export function useHideOnClickOutside({
  dialogRef,
  visibleRef,
  hideOnClickOutsideRef,
  triggerElementRef,
  hideRef,
}: Props) {
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
    eventType: "click",
    listener: (event: Event) => {
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
    eventType: "focusin",
    listener: (event: Event) => {
      const document = getDocument(dialogRef.value)
      if (event.target !== document) {
        hideRef.value()
      }
    },
    shouldListenRef,
  })
}
