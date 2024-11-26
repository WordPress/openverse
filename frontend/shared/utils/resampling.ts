/**
 * Resizes a given array to consist of more elements than provided. This uses
 * linear interpolation to fill in the gaps.
 *
 * @param data - the list of data points to interpolate
 * @param threshold - the number of expected data points from the array
 * @returns the array with the required number of points
 */
export const upsampleArray = (data: number[], threshold: number): number[] => {
  const linearInterpolate = (before: number, after: number, atPoint: number) =>
    before + (after - before) * atPoint

  const newData = []
  const springFactor = (data.length - 1) / (threshold - 1)
  newData[0] = data[0] // for new allocation
  for (let i = 1; i < threshold - 1; i++) {
    const tmp = i * springFactor
    const before = Math.floor(tmp)
    const after = Math.ceil(tmp)
    const atPoint = tmp - before
    newData[i] = linearInterpolate(data[before], data[after], atPoint)
  }
  newData[threshold - 1] = data[data.length - 1] // for new allocation
  return newData
}

/**
 * Resizes a given array to consist of fewer elements than provided. This uses
 * the Largest Triangle Three Buckets algorithm by Sveinn Steinarsson.
 *
 * @see {@link https://github.com/sveinn-steinarsson/flot-downsample}
 *
 * @param data - the list of data points to interpolate
 * @param threshold - the number of expected data points from the array
 * @returns the array with the required number of points
 */
export const downsampleArray = (data: number[], threshold: number) => {
  const dataLength = data.length

  const sampled = []
  let sampled_index = 0

  // Bucket size, except first and last point
  const every = (dataLength - 2) / (threshold - 2)

  let a = 0
  let max_area_point, max_area, area, next_a

  sampled[sampled_index++] = data[a] // Always add the first point

  for (let i = 0; i < threshold - 2; i++) {
    let avg_x = 0
    let avg_y = 0
    let avg_range_start = Math.floor((i + 1) * every) + 1
    let avg_range_end = Math.floor((i + 2) * every) + 1
    avg_range_end = avg_range_end < dataLength ? avg_range_end : dataLength

    const avg_range_length = avg_range_end - avg_range_start

    for (; avg_range_start < avg_range_end; avg_range_start++) {
      avg_x += avg_range_start
      avg_y += data[avg_range_start]
    }
    avg_x /= avg_range_length
    avg_y /= avg_range_length

    // Get the range for this bucket
    let range_offs = Math.floor(i * every) + 1
    const range_to = Math.floor((i + 1) * every) + 1

    const point_a_x = a
    const point_a_y = data[a]

    max_area = area = -1

    max_area_point = 0
    next_a = 0

    for (; range_offs < range_to; range_offs++) {
      // Calculate triangle area over three buckets
      area =
        Math.abs(
          (point_a_x - avg_x) * (data[range_offs] - point_a_y) -
            (point_a_x - range_offs) * (avg_y - point_a_y)
        ) * 0.5
      if (area > max_area) {
        max_area = area
        max_area_point = data[range_offs]
        next_a = range_offs
      }
    }

    sampled[sampled_index++] = max_area_point
    a = next_a
  }

  sampled[sampled_index++] = data[dataLength - 1] // Always add the last point
  return sampled
}
