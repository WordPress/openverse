/**
 * This file cannot be converted to TypeScript because it's used by the Tailwind config
 */
/** @typedef {'2xl' | 'xl' | 'lg' | 'md' | 'sm' | 'xs'} Breakpoint */

/**
 * Mapping of a breakpoint name to the lower-bound of its screen-width range
 */
const SCREEN_SIZES = new Map(
  /** @type {const} */ ([
    ['2xl', 1536],
    ['xl', 1280],
    ['lg', 1024],
    ['md', 768],
    ['sm', 640],
  ])
)

const viewportEntries = [
  ...Array.from(SCREEN_SIZES),
  /** @type {const} */ (['xs', 340]),
].map(([key, val]) => {
  return /** @type {const} */ ([
    key,
    {
      name: `${key} (${val}px)`,
      styles: { width: `${val}px`, height: '768px' },
    },
  ])
})

const VIEWPORTS =
  /** @type {Record<Breakpoint, typeof viewportEntries[number][1]>} */ (
    Object.fromEntries(viewportEntries)
  )

/**
 * This module is consumed by Nuxt and Tailwind config so it needs to use CJS modules
 */
module.exports = {
  SCREEN_SIZES,
  VIEWPORTS,
}
