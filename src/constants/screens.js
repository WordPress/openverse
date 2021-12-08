/**
 * Mapping of a breakpoint name to the lower-bound of its screen-width range
 * @type {Map<string, number>}
 */
export const SCREEN_SIZES = new Map()
SCREEN_SIZES.set('2xl', 1536)
SCREEN_SIZES.set('xl', 1280)
SCREEN_SIZES.set('lg', 1024)
SCREEN_SIZES.set('md', 768)
SCREEN_SIZES.set('sm', 640)

/**
 * Get the breakpoint in which the screen with the given width lies.
 * @param {number} screenWidth - the width of the screen
 * @returns {string} the breakpoint in which the screen lies
 */
export const getBreakpointName = (screenWidth) => {
  for (const [breakpointName, lowerLimit] of SCREEN_SIZES) {
    if (screenWidth >= lowerLimit) {
      return breakpointName
    }
  }
  return 'mob' // smallest breakpoint
}
