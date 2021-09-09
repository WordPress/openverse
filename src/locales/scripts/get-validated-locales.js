const fs = require('fs')
const localesList = require('./locales-list.json')

/** Build the ISO string for a locale */
/** TODO: Move! */
const buildISO = (locale) => {
  let iso = `${locale.lang_code_iso_639_1}`
  if (locale.lang_code_iso_639_2) {
    iso = `${iso}-${locale.lang_code_iso_639_2.toUpperCase()}`
  }
  return iso
}

const getValidatedLocales = () => {
  return Object.values(localesList)
    .map((locale) => ({
      code: locale.slug,
      name: locale.english_name,
      iso: buildISO(locale),
      file: `${locale.slug}.json`,
    }))
    .filter((i) => fs.existsSync(process.cwd() + `/src/locales/${i.file}`))
}

console.log(process.cwd())

try {
  let locales = getValidatedLocales()
  const fileName = 'valid-locales.json'
  fs.writeFileSync(
    process.cwd() + `/src/locales/scripts/` + fileName,
    JSON.stringify(locales, null, 2) + '\n'
  )
  console.log(`> Wrote locale metadata for @nuxt/i18n.`)
} catch (err) {
  console.error(err)
}
