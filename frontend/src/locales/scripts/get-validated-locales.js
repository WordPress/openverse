/*
Updates the translation status of locales list from wp-locales-list,
and saves lists of translated and untranslated locales with properties expected
by Vue i18n.
 */
const fs = require("fs")

const localesList = require("./wp-locales.json")
const { addFetchedTranslationStatus } = require("./get-translations-status")

/**
 * Returns a list of locale objects with at least one translated string
 * @returns {{
 * translated: import('./types').I18nLocaleProps[],
 * untranslated: import('./types').I18nLocaleProps[]
 * }}
 */
const getValidatedLocales = async () => {
  const result = {
    translated: [],
    untranslated: [],
  }
  const updatedLocaleList = await addFetchedTranslationStatus(localesList)
  const allLocales = Object.values(updatedLocaleList).map((locale) => ({
    /* Nuxt i18n fields */

    code: locale.slug,
    dir: locale.textDirection || "ltr",
    file: `${locale.slug}.json`,
    iso: locale.langCodeIso_639_1 ?? undefined,

    /* Custom fields */

    name: locale.name,
    nativeName: locale.nativeName || locale.name,
    translated: locale.translated,
  }))
  for (const locale of allLocales) {
    const fileLocation = `${process.cwd()}/src/locales/${locale.file}`
    if (fs.existsSync(fileLocation)) {
      result.translated.push(locale)
    } else {
      result.untranslated.push(locale)
    }
  }
  return result
}

try {
  getValidatedLocales().then((locales) => {
    const fileName = "valid-locales.json"
    fs.writeFileSync(
      process.cwd() + `/src/locales/scripts/` + fileName,
      JSON.stringify(locales.translated, null, 2) + "\n"
    )
    const untranslatedFileName = "untranslated-locales.json"
    fs.writeFileSync(
      process.cwd() + `/src/locales/scripts/` + untranslatedFileName,
      JSON.stringify(locales.untranslated, null, 2) + "\n"
    )
    console.log(`> Wrote locale metadata for @nuxt/i18n.`)
  })
} catch (err) {
  console.error(err)
}
