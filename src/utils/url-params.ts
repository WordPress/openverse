/**
 * Gets the value of the query parameter from a URL. If the key contains
 * multiple values, they are joined using commas.
 *
 * @param key - the name of the parameter for which values are to be extracted
 * @param url - the URL containing query parameters
 */
export const getParameterByName = (key: string, url: string): string => {
  const name = key.replace(/[[\]]/g, '\\$&')
  const regex = new RegExp(`(${name})=([^&]*)+&*`, 'g')

  const parameterValues = []
  let regexResults = regex.exec(url)

  while (regexResults) {
    const value = decodeURIComponent(regexResults[2].replace(/\+/g, ' '))
    parameterValues.push(value)

    regexResults = regex.exec(url)
  }

  return parameterValues.join(',')
}
