const axios = require("./axios")
const { writeLocaleFile } = require("./utils")
const jed1xJsonToJson = require("./jed1x-json-to-json")

const DOWNLOAD_BASE_URL =
  "https://translate.wordpress.org/projects/meta/openverse"

const getTranslationUrl = (locale) =>
  `${DOWNLOAD_BASE_URL}/${locale}/default/export-translations/`

const fetchJed1x = async (locale) => {
  try {
    const res = await axios.get(getTranslationUrl(locale), {
      params: { format: "jed1x" },
    })
    return res.data
  } catch (err) {
    return err.response.status
  }
}

const isEmpty = (obj) => Object.values(obj).every((x) => x === null)

const fetchJed1xAll = async (locales) => {
  const results = await Promise.allSettled(locales.map(fetchJed1x))

  let succeeded = {}
  let failed = {}
  results.forEach(({ status, value }, index) => {
    if (status === "fulfilled" && !isEmpty(value)) {
      succeeded[locales[index]] = jed1xJsonToJson(value)
    } else {
      failed[locales[index]] = value
    }
  })
  await Promise.all(
    Object.entries(succeeded).map((args) => writeLocaleFile(...args))
  )

  return [Object.keys(succeeded).length, Object.keys(failed).length]
}

const separateDownload = async () => {
  console.log("Performing parallel download.")

  const localeJson = require("./wp-locales.json")
  const locales = Object.values(localeJson).map((item) => item.slug)
  const [succeeded, failed] = await fetchJed1xAll(locales)

  console.log(`Successfully downloaded ${succeeded} translations.`)
  if (failed) {
    console.log(`Failed to download ${failed} translations.`)
    throw new Error("Parallel download partially failed")
  }
}

module.exports = separateDownload
