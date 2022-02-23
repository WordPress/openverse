/**
 * decodes some edge cases of Unicode characters with an extra \
 * See test cases for some examples
 * @param {string} [data]
 */
export default function decodeData(data) {
  if (data) {
    try {
      const regexASCII = /\\x([\d\w]{2})/gi
      const ascii = data.replace(regexASCII, (_, grp) =>
        String.fromCharCode(parseInt(grp, 16))
      )
      const regexUni = /\\u([\d\w]{4})/gi
      const uni = ascii.replace(regexUni, (_, grp) =>
        String.fromCharCode(parseInt(grp, 16))
      )
      return decodeURI(uni)
    } catch (e) {
      return data
    }
  }
  return ''
}
