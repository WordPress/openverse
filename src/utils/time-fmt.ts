/**
 * Format the time as hh:mm:ss, dropping the hour part if it is zero. Unless
 * specified to be milliseconds, the duration is assumed to be in seconds.
 *
 * @param duration - the duration to format as a human-readable timestamp
 * @param isMs - whether the duration is in milliseconds
 * @returns the duration in a human-friendly format
 */
export const timeFmt = (duration: number, isMs = false): string => {
  const seconds = isMs ? duration / 1e3 : duration

  const hrs = ~~(seconds / 3600)
  let mins = (~~((seconds % 3600) / 60)).toString()
  const secs = (~~seconds % 60).toString().padStart(2, "0") // always padded

  const parts = []
  if (hrs > 0) {
    parts.push(hrs)
    mins = mins.padStart(2, "0") // padded only if hours present
  }
  parts.push(mins, secs)
  return parts.join(":")
}
