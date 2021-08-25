/**
 * Fetch the NGX-Translate JSON file for each supported language,
 * convert to our JSON format, and save in the correct folder.
 */
const { writeFile } = require('fs/promises')
const fetch = require('node-fetch')
const ngxJsonToJson = require('./ngx-json-to-json')

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
const makeTranslationUrl = (format = 'po') => (localeCode = 'en-gb') =>
  `${baseUrl}/${localeCode}/default/export-translations/?format=${format}`

/**
 * fetch a json translation from GlotPress
 * @param {string} locale
 */
function fetchJSONTranslation(locale) {
  return fetch(makeTranslationUrl('ngx')(locale)).then((res) => res.json())
}

/**
 * Write translation strings to a file in the locale directory
 * @param {string} locale
 * @param {any} translations
 */
function writeLocaleFile(locale, translations) {
  return writeFile(
    process.cwd() + `/src/locales/${locale}.json`,
    JSON.stringify(translations, null, 2)
  )
}

/**
 * Write a file for each translation object
 * @param {{[locale: string]: {[translation: string]: string}}} translationsByLocale
 */
async function writeLocaleFiles(translationsByLocale) {
  return await Promise.all(
    Object.entries(translationsByLocale).map(([locale, translations]) =>
      writeLocaleFile(locale, translations)
    )
  )
}

/**
 * Write translation files to the "src/locales" directory from
 * the supplied list of locales
 *
 * Logs output if you'd like to test:
 * node get-translations.js | jq
 *
 * @param {string[]} locales
 */
const fetchAndConvertNGXTranslations = (locales) =>
  Promise.all(locales.map(fetchJSONTranslation))
    .then((res) => res.map(ngxJsonToJson))
    .then((res) =>
      // Key translations by their locale, i.e { es: translations, es-ve: translations }
      res.reduce((acc, i, index) => ({ ...acc, [locales[index]]: i }), {})
    )
    .then((res) => {
      writeLocaleFiles(res)
      return res
    })

fetchAndConvertNGXTranslations(['es', 'es-ve'])
  .then(console.log)
  .catch(console.error)
