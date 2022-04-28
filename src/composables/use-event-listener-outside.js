import { watch, ref } from '@nuxtjs/composition-api'
import { contains } from 'reakit-utils/contains'

import { getDocument } from '~/utils/dom/get-document'

/**
 * @param {Element} target
 */
function isInDocument(target) {
  const document = getDocument(target)
  if (target.tagName === 'HTML') return true
  return contains(document.body, target)
}

/**
 * @typedef Props
 * @property {import('./types').Ref<HTMLElement>} containerRef
 * @property {import('./types').Ref<HTMLElement>} triggerRef
 * @property {string} eventType
 * @property {(e: Event) => void} listener
 * @property {import('./types').Ref<boolean>} [shouldListenRef]
 */

/**
 * @param {Props} props
 */
export const useEventListenerOutside = ({
  containerRef,
  triggerRef,
  eventType,
  listener,
  shouldListenRef,
}) => {
  const boundEventRef = ref()

  watch(
    /** @type {const} */ ([
      containerRef,
      triggerRef,
      shouldListenRef || ref(false),
    ]),
    ([container, trigger, shouldListen], _, onInvalidate) => {
      if (boundEventRef.value && !shouldListen) {
        const document = getDocument(container)
        document.removeEventListener(eventType, boundEventRef.value)
      }

      if (!shouldListen) return

      /**
       * @param {Event} event
       */
      const onEvent = (event) => {
        if (!listener || !container || !(event.target instanceof Element))
          return
        const target = event.target

        // When an element is unmounted right after it receives focus, the focus
        // event is triggered after that, when the element isn't part of the
        // current document anymore. So we ignore it.
        if (!isInDocument(target)) return
        // Event inside the container
        if (contains(container, target)) return
        // Event on the trigger
        if (trigger && contains(trigger, target)) return

        listener(event)
      }

      boundEventRef.value = onEvent

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
