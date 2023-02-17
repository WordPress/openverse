const { pipeline } = require("stream/promises")

const { createWriteStream } = require("fs")

const qs = require("qs")
const AdmZip = require("adm-zip")

const { writeLocaleFile } = require("./utils")
const axios = require("./axios")
const jed1xJsonToJson = require("./jed1x-json-to-json")

const LOGIN_URL = "https://login.wordpress.org/wp-login.php"
const BULK_DOWNLOAD_URL =
  "https://translate.wordpress.org/exporter/meta/openverse/-do/"

/**
 * Given a username and password, login to WordPress and get the authentication
 * cookies from the `Set-Cookie` header.
 *
 * @param log {string} - the username to log in with
 * @param pwd {string} - the password for the given username
 * @return {Promise<string[]>} - the list of cookies in the `Set-Cookie` header
 */
const getAuthCookies = async (log, pwd) => {
  const res = await axios.post(
    LOGIN_URL,
    qs.stringify({
      log,
      pwd,
      rememberme: "forever",
      "wp-submit": "Log In",
      redirect_to: "https://make.wordpress.org/",
    }),
    {
      headers: { "content-type": "application/x-www-form-urlencoded" },
      maxRedirects: 0,
      validateStatus: () => true,
    }
  )
  if (
    res.status == 302 &&
    res.headers["set-cookie"].join(" ").includes("wporg_logged_in")
  ) {
    return res.headers["set-cookie"].map((cookie) =>
      cookie.substring(0, cookie.indexOf(";"))
    )
  }
  throw new Error(`Authentication failed: server returned ${res.status}`)
}

/**
 * Fetch the ZIP of translations strings from GlotPress using the authentication
 * cookies to access the page.
 *
 * @param cookies {string[]} - the cookies to authenticate the ZIP download
 * @return {Promise<string>}} - the path to the downloaded ZIP file
 */
const fetchBulkJed1x = async (cookies) => {
  const res = await axios.get(BULK_DOWNLOAD_URL, {
    headers: { cookie: cookies.join(";") },
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
 * Perform a bulk download of translation strings from GlotPress and extrat the
 * JSON files from the ZIP archive.
 *
 * @return {Promise<boolean>} - whether the bulk download succeeded
 */
const bulkDownload = async () => {
  console.log("Performing bulk download.")
  const username = process.env.GLOTPRESS_USERNAME
  const password = process.env.GLOTPRESS_PASSWORD

  if (!(username && password)) {
    console.log("Auth credentials not found, bulk download cancelled.")
    throw new Error("Bulk download cancelled")
  }

  const cookies = await getAuthCookies(username, password)
  const zipPath = await fetchBulkJed1x(cookies)
  const translations = await extractZip(zipPath)
  console.log(`Successfully saved ${translations.length} translations.`)
}

module.exports = bulkDownload
