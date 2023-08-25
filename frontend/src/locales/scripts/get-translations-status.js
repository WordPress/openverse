/**
 * Fetch the list of locales that are available on translate.wordpress.org
 * and the translation status for all of them.
 * Update the GP locales object with this data, and removes any of the GP
 * locales that are not available on translate.wordpress.org.
 */
const parser = require("node-html-parser")

const axios = require("./axios")

const baseUrl = "https://translate.wordpress.org/projects/meta/openverse/"

function parseRow(row) {
  const cells = row.querySelectorAll("td")
  const langName = cells[0].querySelector("a").text.trim()
  const percentTranslated = parseInt(cells[1].text.trim().replace("%", ""), 10)
  return [langName, percentTranslated]
}

/**
 * Takes an object with all gpLocales, and filters it to return only the locales
 * available at translate.wordpress.org. Also, adds the `code` (the same as GlotPress
 * `slug`), and `translated` with the percentage of translated strings, to each
 * locale object.
 */
const addFetchedTranslationStatus = async (gpLocales) => {
  const raw = await axios.get(baseUrl)
  const parsed = parser.parse(raw.data)
  const langPercent = Object.fromEntries(
    parsed.querySelector("tbody").querySelectorAll("tr").map(parseRow)
  )

  return Object.fromEntries(
    Object.entries(gpLocales)
      .filter(([, langObject]) =>
        Object.hasOwnProperty.apply(langPercent, [langObject.name])
      )
      .map(([langKey, langObject]) => [
        langKey,
        {
          ...langObject,
          translated: langPercent[langObject.name],
        },
      ])
  )
}

module.exports = { addFetchedTranslationStatus }
