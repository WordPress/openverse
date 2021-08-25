/**
 * Fetch the NGX-Translate JSON file for each supported language,
 * convert to our JSON format, and save in the correct folder.
 */
const { writeFile } = require('fs/promises')
const os = require('os')
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
const fetchNgxTranslation = (locale) =>
  fetch(makeTranslationUrl('ngx')(locale)).then((res) => res.json())

/**
 * Write translation strings to a file in the locale directory
 * @param {string} locale
 * @param {any} translations
 */
const writeLocaleFile = (locale, translations) =>
  writeFile(
    process.cwd() + `/src/locales/${locale}.json`,
    JSON.stringify(translations, null, 2) + os.EOL
  )

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

/**
 * Write translation files to the "src/locales" directory from
 * the supplied list of locales
 *
 * @param {string[]} locales
 */
const fetchAndConvertNGXTranslations = (locales) =>
  Promise.all(locales.map(fetchNgxTranslation))
    .then((res) => res.map(ngxJsonToJson))
    .then((res) =>
      // Key translations by their locale, i.e { es: translations, es-ve: translations }
      res.reduce((acc, i, index) => ({ ...acc, [locales[index]]: i }), {})
    )
    .then(writeLocaleFiles)

fetchAndConvertNGXTranslations(['es', 'es-ve']).then().catch(console.error)
