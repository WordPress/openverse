const double_backslash_escaped_regex = /(\\x)([\da-f]{2})|(\\u)([\da-f]{4})/gi
const no_backslash_escaped_regex = /(?<!\\)(u)([\da-f]{4})/gi

const encodeGroup = (prefix: string, group: string) => {
  try {
    const encoded = String.fromCharCode(parseInt(group, 16))
    encodeURIComponent(encoded)
    return decodeURI(encoded)
  } catch {
    return prefix + group
  }
}

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

  const decodedData = data.replace(
    double_backslash_escaped_regex,
    (_match, g1, g2, g3, g4) => {
      return encodeGroup(g1 || g3, g2 || g4)
    }
  )
  if (decodedData === data) {
    return data.replace(no_backslash_escaped_regex, (_match, g1, g2) => {
      return encodeGroup(g1, g2)
    })
  }
  return decodedData
}
