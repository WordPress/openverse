import { Ref, ref, watch } from "vue"

import { contains, getDocument, isInDocument } from "~/utils/reakit-utils/dom"

interface Props {
  /**
   * A click outside of this element will trigger the `listener` function.
   */
  containerRef: Ref<HTMLElement | null>
  /**
   * The element that triggers the dialog and will be focused when modal is closed.
   */
  triggerRef: Ref<HTMLElement | null>
  /**
   * The type of event to listen to.
   */
  eventType: string
  /**
   * The function to be called on a click outside of the `containerRef` element
   * @param e - the event object
   */
  listener: (e: Event) => void
  /**
   * Whether the listener should be active or not.
   */
  shouldListenRef?: Ref<boolean>
}

export const useEventListenerOutside = ({
  containerRef,
  triggerRef,
  eventType,
  listener,
  shouldListenRef,
}: Props) => {
  const boundEventRef = ref()

  watch(
    [containerRef, triggerRef, shouldListenRef || ref(false)] as const,
    ([container, trigger, shouldListen], _, onInvalidate) => {
      if (boundEventRef.value && !shouldListen) {
        const document = getDocument(container)
        document.removeEventListener(eventType, boundEventRef.value)
      }

      if (!shouldListen) {
        return
      }

      boundEventRef.value = (event: Event) => {
        if (!listener || !container || !(event.target instanceof Element)) {
          return
        }
        const target = event.target

        // When an element is unmounted right after it receives focus, the focus
        // event is triggered after that, when the element isn't part of the
        // current document anymore. So we ignore it.
        if (!isInDocument(target)) {
          return
        }
        // Event inside the container
        if (contains(container, target)) {
          return
        }
        // Event on the trigger
        if (trigger && contains(trigger, target)) {
          return
        }

        listener(event)
      }

      const document = getDocument(container)
      document.addEventListener(eventType, boundEventRef.value)
      onInvalidate(() => {
        if (boundEventRef.value) {
          document.removeEventListener(eventType, boundEventRef.value)
          boundEventRef.value = undefined
        }
      })
    },
    { immediate: true }
  )
}
