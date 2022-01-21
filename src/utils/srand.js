/**
 * Seeded random number generator.
 * Taken from https://github.com/micro-js/srand/blob/master/lib/index.js
 */

module.exports = srand

/**
 * srand
 */
function srand(seed) {
  let str
  // If we're passed a string, condense it down
  // into a number
  if (typeof seed === 'string') {
    str = seed
    seed = 0xff
    for (var i = 0; i < str.length; i++) {
      seed ^= str.charCodeAt(i)
    }
  }

  return function (max, min) {
    max = max || 1
    min = min || 0
    seed = (seed * 9301 + 49297) % 233280

    return min + (seed / 233280) * (max - min)
  }
}
