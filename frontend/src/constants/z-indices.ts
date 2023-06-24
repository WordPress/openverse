
export const Z_INDICES: { [key: string]: string | number } = Object.freeze({
  auto: "auto",
  10: 10,
  20: 20,
  30: 30,
  40: 40,
  50: 50,
  // Named indices
  popover: 50,
  snackbar: 10,
  "global-audio": 20,
} as const)

/**
 * Check whether the given z-index is valid and is configured in Tailwind.
 *
* @param value - the provided z-index to validate
* @return whether the z-index is valid and configured in Tailwind
*/
export const zIndexValidator = (value: string | number): boolean =>
Object.keys(Z_INDICES).includes(value.toString())


