/**
 * Convert the given value, string or boolean, to a boolean value by casting
 * - `'true'`, `'yes'` and `'1'` to true
 * - `'false'`, `'no'` and `'0'` to false
 *
 * Any other string will be cast to boolean using the default JavaScript
 * truthy-falsy logic.
 *
 * @param value - the value to cast
 * @returns the boolean-equivalent value of the given string or boolean
 */
export const stringToBoolean = (value: string | boolean): boolean => {
  // In case the string is already a boolean, return as-is.
  // If `.env` vars are auto-cast to booleans, this will catch that.
  if (typeof value === "boolean") {
    return value
  }

  if (!value) {
    return false
  }

  value = value.toLowerCase().trim()
  switch (value) {
    case "true":
    case "yes":
    case "1": {
      return true
    }
    case "false":
    case "no":
    case "0": {
      return false
    }
    default: {
      return Boolean(value)
    }
  }
}
