/**
 * mapping of z-index names to z-indices; Ensure that these values are also
 * written in the `tailwind.safelist.txt` file in the project root.
 */
export const Z_INDICES = Object.freeze({
  auto: "auto",
  10: "10",
  20: "20",
  30: "30",
  40: "40",
  50: "50",
  // Named indices
  popover: "50",
  snackbar: "10",
  "global-audio": "20",
} as const)

/**
 * Check whether the given z-index is valid and is configured in Tailwind.
 *
 * @param value - the provided z-index to validate
 * @returns - whether the z-index is valid and configured in Tailwind
 */
export const zIndexValidator = (value: string | number): boolean =>
  Object.keys(Z_INDICES).includes(value.toString())

export type ZIndex = keyof typeof Z_INDICES
