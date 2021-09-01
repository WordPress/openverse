// locales.py
// This script extracts data for locales available in GlotPress, and
// saves it to `locales-list.json`

const axios = require('axios')
const fs = require('fs')

const base_url =
  'https://raw.githubusercontent.com/GlotPress/GlotPress-WP/develop/locales/locales.php'

const locales = {}

async function getLocalesData() {
  const res = await axios.get(base_url)
  return res.data
}

getLocalesData()
  .then((data) => {
    const rawLocalesData = data
      .split('new GP_Locale();')
      .splice(1)
      .map((item) => item.trim())

    const properties = [
      'english_name',
      'native_name',
      'lang_code_iso_639_1',
      'lang_code_iso_639_2',
      'country_code',
      'slug',
      'nplurals',
      'plural_expression',
      'google_code',
      'facebook_locale',
    ]
    const propertyRePatterns = {}
    properties.forEach((prop) => {
      propertyRePatterns[prop] = new RegExp(`${prop} *= *['](.*)['];`)
    })

    const wpLocalePattern = /wp_locale *= *'(.*)';/
    rawLocalesData.forEach((rawData) => {
      const wpLocaleMatch = rawData.match(wpLocalePattern)
      // ugly check to exclude English from the locales list, so we don't overwrite `en.json` later.
      if (wpLocaleMatch && wpLocaleMatch[1] !== 'en_US') {
        const wpLocale = wpLocaleMatch[1]
        locales[wpLocale] = {}
        Object.keys(propertyRePatterns).forEach((key) => {
          const pattern = propertyRePatterns[key]
          const value = rawData.match(pattern)
          if (value) {
            locales[wpLocale][key] = value[1]
          }
        })
      }
    })

    try {
      const fileName = process.cwd() + '/src/locales/scripts/locales-list.json'
      fs.writeFileSync(fileName, JSON.stringify(locales, null, 2))
      console.log(`Successfully wrote locales list file to ${fileName}`)
    } catch (err) {
      console.error(err)
    }
  })
  .catch((err) => console.log('Could not fetch data from ', base_url, err))
