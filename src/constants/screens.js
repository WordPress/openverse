/** @typedef {'2xl' | 'xl' | 'lg' | 'md' | 'sm' | 'xs' | 'mob'} Breakpoints */

/**
 * Mapping of a breakpoint name to the lower-bound of its screen-width range
 * @type {Map<Exclude<Breakpoints, 'mob'>, number>}
 */
const SCREEN_SIZES = new Map([
  ['2xl', 1536],
  ['xl', 1280],
  ['lg', 1024],
  ['md', 768],
  ['sm', 640],
  ['xs', 340],
])

const VIEWPORTS = Object.fromEntries(
  [...Array.from(SCREEN_SIZES), ['mob', 400]].map(([key, val]) => {
    return [
      key,
      {
        name: `${key} (${val}px)`,
        styles: { width: `${val}px`, height: '768px' },
      },
    ]
  })
)

/**
 * Get the breakpoint in which the screen with the given width lies.
 * @param {number} screenWidth - the width of the screen
 * @returns {Breakpoints} the breakpoint in which the screen lies
 */
const getBreakpointName = (screenWidth) => {
  for (const [breakpointName, lowerLimit] of SCREEN_SIZES) {
    if (screenWidth >= lowerLimit) {
      return breakpointName
    }
  }
  return 'mob' // smallest breakpoint
}

/**
 * This module is consumed by Nuxt and Tailwind config so it needs to use CJS modules
 */
module.exports = {
  SCREEN_SIZES,
  VIEWPORTS,
  getBreakpointName,
}
