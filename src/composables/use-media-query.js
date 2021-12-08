/* this implementation is from https://github.com/vueuse/vueuse/packages/core/useMediaQuery/
 which, in turn, is ported from https://github.com/logaretm/vue-use-web by Abdelrahman Awad */
import { onBeforeUnmount, ref } from '@nuxtjs/composition-api'
import { SCREEN_SIZES } from '~/constants/screens.js'

/**
 * Reactive Media Query.
 *
 * @param query
 * @param options
 */
export function useMediaQuery(query, options = {}) {
  const { window } = options
  if (!window) return ref(false)

  const mediaQuery = window.matchMedia(query)
  /** @type {import('@nuxtjs/composition-api').Ref<boolean>} */
  const matches = ref(mediaQuery.matches)

  const handler = (/** @type MediaQueryListEvent */ event) => {
    matches.value = event.matches
  }
  // Before Safari 14, MediaQueryList is based on EventTarget,
  // so we use addListener() and removeListener(), too.
  if ('addEventListener' in mediaQuery) {
    mediaQuery.addEventListener('change', handler)
  } else {
    mediaQuery.addListener(handler)
  }

  onBeforeUnmount(() => {
    if ('removeEventListener' in mediaQuery) {
      mediaQuery.removeEventListener('change', handler)
    } else {
      mediaQuery.removeListener(handler)
    }
  })

  return matches
}

/**
 * Check whether the screen meets the current breakpoint size.
 */
export const isScreen = (breakpointName, options = {}) => {
  return useMediaQuery(
    `(min-width: ${SCREEN_SIZES.get(breakpointName)}px)`,
    options
  )
}

/**
 * Check if the user prefers reduced motion or not.
 */
export function useReducedMotion(options = {}) {
  return useMediaQuery('(prefers-reduced-motion: reduce)', options)
}
