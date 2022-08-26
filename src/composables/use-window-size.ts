/**
 * Code from Vueuse project:
 * https://github.com/vueuse/vueuse/blob/1eb83c41bb1ca6e6c8ee61c46ce9dbca7ab1613f/packages/core/useWindowSize/index.ts
 */
import { getCurrentInstance, onMounted, ref } from '@nuxtjs/composition-api'

import { defaultWindow } from '~/constants/window'
import { useEventListener } from '~/composables/use-event-listener'

export interface UseWindowSizeOptions {
  initialWidth?: number
  initialHeight?: number
  /**
   * Listen to window `orientationchange` event
   */
  listenOrientation?: boolean
  window?: Window
}

/**
 * Reactive window size.
 **/
export function useWindowSize(options: UseWindowSizeOptions = {}) {
  const {
    window = defaultWindow,
    initialWidth = Infinity,
    initialHeight = Infinity,
    listenOrientation = true,
  } = options

  const width = ref(initialWidth)
  const height = ref(initialHeight)

  const update = () => {
    if (window) {
      width.value = window.innerWidth
      height.value = window.innerHeight
    }
  }

  update()
  // Run onMounted after the initial render, if inside a component lifecycle
  if (getCurrentInstance()) {
    onMounted(update)
  }
  if (!window) return { width, height }
  useEventListener(window, 'resize', update, { passive: true })

  if (listenOrientation)
    useEventListener(window, 'orientationchange', update, { passive: true })

  return { width, height }
}

export type UseWindowSizeReturn = ReturnType<typeof useWindowSize>
