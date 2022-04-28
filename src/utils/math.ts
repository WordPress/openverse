/**
 * Math utilities
 */

export type Point = [number, number]

/**
 * Perform linear interpolation to find a value that is fractionally between
 * the low and high limits of the given range.
 *
 * @param low - the lower limit of the range
 * @param high - the upper limit of the range
 * @param frac - fraction controlling position of interpolated number
 * @returns the interpolated number
 */
export const lerp = (low: number, high: number, frac: number): number =>
  low + (high - low) * frac

/**
 * Interpolate twice to solve the Bézier equation for three points P0, P1
 * and P2.
 *
 * @param p0 - point #0
 * @param p1 - point #1
 * @param p2 - point #2
 * @param frac - the fraction at which to solve the Bézier equation
 * @returns a solution to the 3-point Bézier equation
 */
export const doubleLerp = (
  p0: Point,
  p1: Point,
  p2: Point,
  frac: number
): Point => [
  lerp(lerp(p0[0], p1[0], frac), lerp(p1[0], p2[0], frac), frac),
  lerp(lerp(p0[1], p1[1], frac), lerp(p1[1], p2[1], frac), frac),
]

/**
 * Find the distance between two points P0 and P1.
 *
 * @param p0 - point #0
 * @param p1 - point #1
 * @returns the distance between the two points
 */
export const dist = (p0: Point, p1: Point): number =>
  Math.sqrt(Math.pow(p0[0] - p1[0], 2) + Math.pow(p0[1] - p1[1], 2))

/**
 * Get the required number of x-coordinates of Bézier points using 4 control
 * points.
 *
 * @param ctrlPts - the array of control points
 * @param pointCount - the number of Bézier points to calculate
 * @returns the list of x-coordinates of Bézier points
 */
export const bezier = (ctrlPts: Point[], pointCount: number): number[] => {
  const bezierPoints = []
  for (let i = 0; i <= pointCount; i++) {
    const frac = i / pointCount
    const a = doubleLerp(ctrlPts[0], ctrlPts[1], ctrlPts[2], frac)
    const b = doubleLerp(ctrlPts[1], ctrlPts[2], ctrlPts[3], frac)
    const x = lerp(a[0], b[0], frac)
    bezierPoints.push(x)
  }
  return bezierPoints
}
