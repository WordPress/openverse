/**
 * Fetch the NGX-Translate JSON file for each supported language,
 * convert to our JSON format, and save in the correct folder.
 */
const { writeFile } = require('fs/promises')
const { writeFileSync } = require('fs')
const os = require('os')

const chokidar = require('chokidar')

const axios = require('./axios')

const jed1xJsonToJson = require('./jed1x-json-to-json')
const { parseJson } = require('./read-i18n')

/**
 *
 * @typedef {"json"|"jed1x"|"ngx"} JSONFormat
 * @returns
 */

/**
 * A GlotPress Output format for translation strings
 * @typedef {("android"|"po"|"mo"|"resx"|"strings"|"properties"|"json"|"jed1x"|"ngx" & JSONFormat)} Format
 */

const baseUrl = `https://translate.wordpress.org/projects/meta/openverse`

/**
 *
 * @param {Format} format
 * @returns {(localeCode: string) => string}
 */
const makeTranslationUrl =
  (format = 'po') =>
  (localeCode = 'en-gb') =>
    `${baseUrl}/${localeCode}/default/export-translations/?format=${format}`

/**
 * fetch a json translation from GlotPress
 * @param {string} locale
 */
const fetchJed1xTranslation = (locale) =>
  axios.get(makeTranslationUrl('jed1x')(locale)).then((res) => res.data)

const replacePlaceholders = (json) => {
  if (json === null) {
    return null
  }
  if (typeof json === 'string') {
    return json.replace(/###([a-zA-Z-]*)###/g, '{$1}')
  }
  let currentJson = { ...json }

  for (const row of Object.entries(currentJson)) {
    let [key, value] = row
    currentJson[key] = replacePlaceholders(value)
  }
  return currentJson
}
/**
 * Write translation strings to a file in the locale directory
 * @param {string} locale
 * @param {any} rawTranslations
 */
const writeLocaleFile = (locale, rawTranslations) => {
  const translations = replacePlaceholders(rawTranslations)
  return writeFile(
    process.cwd() + `/src/locales/${locale}.json`,
    JSON.stringify(translations, null, 2) + os.EOL
  )
}

/**
 * Write a file for each translation object
 * @param {{[locale: string]: {[translation: string]: string}}} translationsByLocale
 */
const writeLocaleFiles = (translationsByLocale) =>
  Promise.all(
    Object.entries(translationsByLocale).map(([locale, translations]) =>
      writeLocaleFile(locale, translations)
    )
  )

// Check if an object is empty
const isEmpty = (obj) => Object.values(obj).every((x) => x === null)

/**
 * Write translation files to the "src/locales" directory from
 * the supplied list of locales
 *
 * @param {string[]} locales
 */
const fetchAndConvertJed1xTranslations = (locales) => {
  return Promise.allSettled(locales.map(fetchJed1xTranslation))
    .then((res) => {
      let successfulTranslations = []
      res.forEach(({ status, value }, index) => {
        if (status === 'fulfilled' && !isEmpty(value)) {
          successfulTranslations[locales[index]] = value
        }
      })
      return successfulTranslations
    })
    .then((res) => {
      Object.keys(res).forEach((key) => {
        res[key] = jed1xJsonToJson(res[key])
      })
      return res
    })
    .then(writeLocaleFiles)
}

/**
 * Write `en.json` from `en.json5`.
 */
const writeEnglish = () => {
  const rootEntry = parseJson('en.json5')
  writeFileSync(
    process.cwd() + '/src/locales/en.json',
    JSON.stringify(rootEntry, null, 2) + os.EOL
  )
  console.log('Successfully saved English translation to en.json.')
}

writeEnglish()
if (process.argv.includes('--watch')) {
  console.log('Watching en.json5 for changes...')
  chokidar
    .watch(process.cwd() + '/src/locales/scripts/en.json5')
    .on('all', (event, path) => {
      console.log(`Event '${event}' for file ${path}`)
      writeEnglish()
    })
}

if (!process.argv.includes('--en-only')) {
  const localeJSON = require('./wp-locales.json')

  fetchAndConvertJed1xTranslations(Object.values(localeJSON).map((i) => i.slug))
    .then((res) => {
      console.log(`Successfully saved ${res.length + 1} translations.`)
    })
    .catch(console.error)
}
