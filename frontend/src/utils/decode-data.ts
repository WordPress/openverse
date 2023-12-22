/**
 * Decodes some edge cases where ASCII/Unicode characters with escape sequences
 * have escaped backslashes, which prevents them from rendering. This function
 * replaces them with the relevant character.
 *
 * @param data - the string to unescape so that it can be rendered
 */
export const decodeData = (data = ""): string => {
  if (!data) {
    return ""
  }

  try {
    const regexes = [
      /\\x([\da-f]{2})/gi,
      /\\u([\da-f]{4})/gi,
      /u([\da-f]{4})/gi,
    ]
    regexes.forEach((regex) => {
      data = data.replace(regex, (_, grp) =>
        String.fromCharCode(parseInt(grp, 16))
      )
    })
    return decodeURI(data)
  } catch (e) {
    return data
  }
}
