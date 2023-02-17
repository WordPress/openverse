/**
 * Utilities for generating pseudo-random numbers.
 */

/**
 * Small Fast Counter is a seedable pseudo-random number generator. It accepts 4
 * numbers as seeds.
 * @see {@link https://github.com/bryc/code/blob/master/jshash/PRNGs.md#sfc32}
 *
 * @param a - first seed for SFC32
 * @param b - second seed for SFC32
 * @param c - third seed for SFC32
 * @param d - fourth seed for SFC32
 * @returns the seeded PRNG
 */
const sfc32 = (a: number, b: number, c: number, d: number) => (): number => {
  a |= 0
  b |= 0
  c |= 0
  d |= 0
  const t = (((a + b) | 0) + d) | 0
  d = (d + 1) | 0
  a = b ^ (b >>> 9)
  b = (c + (c << 3)) | 0
  c = (c << 21) | (c >>> 11)
  c = (c + t) | 0
  return (t >>> 0) / 4294967296
}

/**
 * Get a seedable pseudo-random number generator based on SFC32 that accepts 1
 * number as the seed. It uses three other arbitrary seeds.
 *
 * @param d - fourth seed for SFC32
 * @returns the seeded PRNG
 */
export const rand = (d: number) => sfc32(0x9e3779b9, 0x243f6a88, 0xb7e15162, d)

/**
 * Hash a string into a 32-bit number that can be used as the seed for a
 * pseudo-random number generator.
 *
 * @param str - the string to hash
 * @returns the number generated from hashing the string
 */
export const hash = (str: string): number => {
  let hash = 0
  if (str.length === 0) {
    return hash
  }
  for (let i = 0; i < str.length; i++) {
    const chr = str.charCodeAt(i)
    hash = (hash << 5) - hash + chr
    hash |= 0 // Convert to 32-bit integer
  }
  return hash
}
