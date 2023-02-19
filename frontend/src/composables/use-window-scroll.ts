// code taken from Vueuse
import { throttle } from "throttle-debounce"
import { ref } from "@nuxtjs/composition-api"

import { defaultWindow } from "~/constants/window"
import { useEventListener } from "~/composables/use-event-listener"

/**
 * Whether the page has been scrolled down at all.
 *
 * This global ref is SSR safe because it will only
 * change internal value based on client side interaction.
 */
const isScrolled = ref(false)

interface UseWindowScrollOptions {
  /**
   * Window from which to read and track scroll position
   */
  window?: typeof defaultWindow | undefined
  /**
   * Time to throttle the scroll handler.
   * Set to 0 to remove throttling.
   */
  throttleMs?: number
}

export function useWindowScroll({
  window = defaultWindow,
  throttleMs = 200,
}: UseWindowScrollOptions = {}) {
  if (!window) {
    // In SSR, no need to track anything.
    return Object.freeze({
      x: ref(0),
      y: ref(0),
      isScrolled,
    })
  }

  const x = ref(0)
  const y = ref(0)

  const scrollHandler = () => {
    x.value = window.scrollX
    y.value = window.scrollY
    isScrolled.value = y.value > 0
  }

  scrollHandler()

  const handler = throttleMs
    ? throttle(throttleMs, scrollHandler)
    : scrollHandler

  useEventListener(window, "scroll", handler, {
    capture: false,
    passive: true,
  })

  return Object.freeze({ x, y, isScrolled })
}
