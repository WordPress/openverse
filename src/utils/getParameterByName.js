export default function getParameterByName(key, url) {
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
