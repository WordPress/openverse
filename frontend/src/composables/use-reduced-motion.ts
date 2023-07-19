import { useMediaQuery } from "@vueuse/core"
/**
 * Check if the user prefers reduced motion or not.
 */
export function useReducedMotion() {
  return useMediaQuery("(prefers-reduced-motion: reduce)")
}
