/**
 * Fetch the list of locales that are available on translate.wordpress.org
 * and the translation status for all of them.
 * Update the GP locales object with this data, and removes any of the GP
 * locales that are not available on translate.wordpress.org.
 */
const parser = require('node-html-parser')

const axios = require('./axios')

const baseUrl = 'https://translate.wordpress.org/projects/meta/openverse/'

function parseRow(row, locales) {
  const cells = row.querySelectorAll('td')
  const langLink = cells[0].querySelector('a')
  const langName = langLink.text.trim()
  const langObject = locales.find((locale) => {
    return locale.name === langName
  })
  if (langObject) {
    const percentTranslated = parseInt(
      cells[1].text.trim().replace('%', ''),
      10
    )
    langObject.code = langObject.slug
    langObject.translated = percentTranslated
    return langObject
  }
}

/**
 * Takes an object with all gpLocales, and filters it to return only the locales
 * available at translate.wordpress.org. Also, adds the `code` (the same as GlotPress
 * `slug`), and `translated` with the percentage of translated strings, to each
 * locale object.
 */
const addFetchedTranslationStatus = async (gpLocales) => {
  const locales = Object.values(gpLocales)

  const localesData = {}
  const raw = await axios.get(baseUrl)

  const parsed = parser.parse(raw.data)
  parsed
    .querySelector('tbody')
    .querySelectorAll('tr')
    .forEach((row) => {
      const locale = parseRow(row, locales)
      if (locale) {
        localesData[locale.wpLocale] = locale
      }
    })
  return localesData
}

module.exports = { addFetchedTranslationStatus }
