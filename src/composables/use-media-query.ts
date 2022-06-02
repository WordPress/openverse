/* this implementation is from https://github.com/vueuse/vueuse/packages/core/useMediaQuery/
 which, in turn, is ported from https://github.com/logaretm/vue-use-web by Abdelrahman Awad */
import { onBeforeUnmount, ref } from '@nuxtjs/composition-api'

import { SCREEN_SIZES, Breakpoint } from '~/constants/screens'
import { defaultWindow } from '~/constants/window'

interface Options {
  shouldPassInSSR?: boolean
  window?: Window
}

/**
 * Reactive Media Query.
 */
export function useMediaQuery(
  query: string,
  options: Options = { shouldPassInSSR: false }
) {
  const matches = ref(false)
  const { window = defaultWindow } = options
  if (!window) {
    matches.value = Boolean(options.shouldPassInSSR)
    return matches
  }

  const mediaQuery = window.matchMedia(query)
  matches.value = mediaQuery.matches

  const handler = (event: MediaQueryListEvent) => {
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
 * Check whether the current screen meets
 * or exceeds the provided breakpoint size.
 */
export const isMinScreen = (breakpointName: Breakpoint, options?: Options) => {
  if (breakpointName === 'xs') {
    // `xs` is the "minimum" so it is always true
    return ref(true)
  }

  return useMediaQuery(
    `(min-width: ${SCREEN_SIZES.get(breakpointName)}px)`,
    options
  )
}

/**
 * Check if the user prefers reduced motion or not.
 */
export function useReducedMotion(options?: Options) {
  return useMediaQuery('(prefers-reduced-motion: reduce)', options)
}
