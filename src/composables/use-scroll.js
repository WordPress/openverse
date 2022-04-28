// code taken from Vueuse
import { throttle } from 'throttle-debounce'
import { ref } from '@nuxtjs/composition-api'

import { useEventListener } from '~/composables/use-event-listener'

/**
 *
 * @param { import('./types').MaybeRef<HTMLElement> } element
 * @param {object} options
 * @param {number} [options.throttleMs] - time to throttle the scroll handler.
 * Set to 0 to remove throttling
 */
export function useScroll(element, { throttleMs = 200 } = {}) {
  /** @type { import('@nuxtjs/composition-api').Ref<number> } */
  const y = ref(0)
  /**
   * Whether the element has been scrolled down at all
   *
   * @type { import('@nuxtjs/composition-api').Ref<boolean> }
   */
  const isScrolled = ref(false)

  if (element) {
    /** @param { Event } e */
    const scrollHandler = (e) => {
      const eventTarget =
        e.target === document ? e.target.documentElement : e.target
      y.value = eventTarget.scrollTop
      isScrolled.value = y.value > 0
    }

    const handler = throttleMs
      ? throttle(throttleMs, scrollHandler)
      : scrollHandler

    useEventListener(element, 'scroll', handler, {
      capture: false,
      passive: true,
    })
  }

  return { y, isScrolled }
}
