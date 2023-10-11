import { useWindowSize, watchDebounced } from "@vueuse/core"

import type { RealBreakpoint } from "~/constants/screens"
import { ALL_SCREEN_SIZES } from "~/constants/screens"
import { useUiStore } from "~/stores/ui"

const widthToBreakpoint = (width: number): RealBreakpoint => {
  const bp = Object.entries(ALL_SCREEN_SIZES).find(
    ([, bpWidth]) => width >= bpWidth
  ) ?? ["xs", 0]
  return bp[0] as RealBreakpoint
}

/**
 * This composable updates the UI store when the screen width changes or
 * when the SSR layout settings are different from the cookie settings.
 */
export function useLayout() {
  const uiStore = useUiStore()

  const { width } = useWindowSize()

  const updateBreakpoint = () => {
    uiStore.updateBreakpoint(widthToBreakpoint(width.value))
  }

  watchDebounced(
    width,
    (newWidth) => {
      const newBp = widthToBreakpoint(newWidth)
      uiStore.updateBreakpoint(newBp)
    },
    { debounce: 100 }
  )

  return {
    updateBreakpoint,
  }
}
