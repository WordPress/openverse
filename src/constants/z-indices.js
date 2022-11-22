/**
 * This file cannot be converted to TypeScript because it's referenced in the
 * Tailwind config.
 */

/**
 * mapping of z-index names to z-indices; Ensure that these values are also
 * written in the `tailwind.safelist.txt` file in the project root.
 */
const Z_INDICES = Object.freeze(
  /** @type {const} */ ({
    auto: 'auto',
    10: 10,
    20: 20,
    30: 30,
    40: 40,
    50: 50,
    // Named indices
    popover: 50,
  })
)

/**
 * Check whether the given z-index is valid and is configured in Tailwind.
 *
 * @param value {string|number} the provided z-index to validate
 * @return {boolean} whether the z-index is valid and configured in Tailwind
 */
const zIndexValidator = (value) =>
  Object.keys(Z_INDICES).includes(value.toString())

/**
 * This module is consumed by Nuxt and Tailwind config, so it needs to use CJS modules.
 */
module.exports = {
  Z_INDICES,
  zIndexValidator,
}
