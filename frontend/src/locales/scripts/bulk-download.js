const { pipeline } = require("stream/promises")

const { createWriteStream } = require("fs")

const AdmZip = require("adm-zip")

const { writeLocaleFile } = require("./utils")
const axios = require("./axios")
const jed1xJsonToJson = require("./jed1x-json-to-json")

const BULK_DOWNLOAD_URL =
  "https://translate.wordpress.org/exporter/meta/openverse/-do/"

/**
 * Fetch the ZIP of translations strings from GlotPress using the authentication
 * cookies to access the page.
 *
 * @return {Promise<string>}} - the path to the downloaded ZIP file
 */
const fetchBulkJed1x = async () => {
  const res = await axios.get(BULK_DOWNLOAD_URL, {
    params: { "export-format": "jed1x" },
    responseType: "stream",
  })
  const destPath = process.cwd() + "/src/locales/openverse.zip"
  await pipeline(res.data, createWriteStream(destPath))
  return destPath
}

/**
 * Extract all JSON file from the given ZIP file. Their names are sanitised to
 * be in the format `<locale_code>.json`.
 *
 * @param zipPath {string} - the path to the ZIP file to extract
 * @return {Promise<unknown[]>} - the outcome of writing all ZIP files
 */
const extractZip = async (zipPath) => {
  const zip = new AdmZip(zipPath, undefined)
  const localeJsonMap = zip
    .getEntries()
    .filter((entry) => entry.entryName.endsWith(".json"))
    .map((entry) => {
      const jed1xObj = JSON.parse(zip.readAsText(entry))
      const vueI18nObj = jed1xJsonToJson(jed1xObj)
      const localeName = entry.name
        .replace("meta-openverse-", "")
        .replace(".jed.json", "")
      return [localeName, vueI18nObj]
    })
  return await Promise.all(
    localeJsonMap.map((args) => writeLocaleFile(...args))
  )
}

/**
 * Perform a bulk download of translation strings from GlotPress and extract the
 * JSON files from the ZIP archive.
 *
 * @return {Promise<boolean>} - whether the bulk download succeeded
 */
const bulkDownload = async () => {
  console.log("Performing bulk download.")
  const zipPath = await fetchBulkJed1x()
  const translations = await extractZip(zipPath)
  console.log(`Successfully saved ${translations.length} translations.`)
}

module.exports = bulkDownload
