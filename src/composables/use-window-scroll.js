// code taken from Vueuse
import { throttle } from 'throttle-debounce'
import { ref } from '@nuxtjs/composition-api'

import { defaultWindow } from '~/constants/window'
import { useEventListener } from '~/composables/use-event-listener'

/**
 * Whether the page has been scrolled down at all.
 *
 * This global ref is SSR safe because it will only
 * change internal value based on client side interaction.
 *
 * @type {import('@nuxtjs/composition-api').Ref<boolean>}
 */
const isScrolled = ref(false)

/**
 *
 * @param {object} options
 * @param {Window} [options.window]
 * @param {number} [options.throttleMs] - time to throttle the scroll handler.
 * Set to 0 to remove throttling
 */
export function useWindowScroll({
  window = defaultWindow,
  throttleMs = 200,
} = {}) {
  if (!window) {
    return {
      x: ref(0),
      y: ref(0),
      isScrolled,
    }
  }

  const x = ref(window.pageXOffset)
  const y = ref(window.pageYOffset)

  const scrollHandler = () => {
    x.value = window.pageXOffset
    y.value = window.pageYOffset
    isScrolled.value = y.value > 0
  }

  const handler = throttleMs
    ? throttle(throttleMs, scrollHandler)
    : scrollHandler

  useEventListener(window, 'scroll', handler, {
    capture: false,
    passive: true,
  })

  return { x, y, isScrolled }
}
