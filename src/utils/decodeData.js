/**
 * decodes some edge cases of Unicode characters with an extra \
 * See test cases for some examples
 * @param {string} data
 */
export default function decodeData(data) {
  if (data) {
    try {
      const regexASCII = /\\x([\d\w]{2})/gi
      const ascii = data.replace(regexASCII, (match, grp) =>
        String.fromCharCode(parseInt(grp, 16))
      )
      const regexUni = /\\u([\d\w]{4})/gi
      const uni = ascii.replace(regexUni, (match, grp) =>
        String.fromCharCode(parseInt(grp, 16))
      )
      const res = decodeURI(uni)
      return res
    } catch (e) {
      return data
    }
  }
  return ''
}
