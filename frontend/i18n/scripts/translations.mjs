import { createWriteStream, readFileSync, unlinkSync } from "fs"
import { basename, join } from "path"
import { pipeline } from "stream/promises"

import AdmZip from "adm-zip"
import json5 from "json5"

import { userAgentHeader } from "../../shared/constants/user-agent.mjs"

import { kebabToCamel, prettify, readToJson, writeJson } from "./utils.mjs"
import {
  enJson as enJsonFile,
  enJson5 as enJson5File,
  localesDir,
} from "./paths.mjs"

const NGX_URL =
  "https://translate.wordpress.org/exporter/meta/openverse/-do/?export-format=ngx"

const fetchBulkNgx = async () => {
  const zipPath = join(localesDir, "openverse.zip")
  const res = await fetch(NGX_URL, { headers: userAgentHeader })

  if (!res.ok) {
    throw new Error(
      `Failed to download translations: ${res.status}, ${res.statusText}`
    )
  }

  // Create write stream
  const fileStream = createWriteStream(zipPath)

  // Use pipeline to handle the stream
  await pipeline(res.body, fileStream)

  return zipPath
}

/**
 * Removes entries with null values from a flat json object.
 * @param {Record<string, string | null>} obj - The object to clean
 * @returns {Record<string, string>} - The cleaned object
 */
const removeNullValues = (obj) => {
  const cleaned = {}

  for (const [key, value] of Object.entries(obj)) {
    if (value !== null) {
      cleaned[key] = value
    }
  }

  return cleaned
}

const issueUrl = "https://github.com/WordPress/openverse/issues/"
const kebabCaseIssue = `${issueUrl}2438`
const invalidPlaceholderIssue = `${issueUrl}5149`

const warnings = {
  kebabCase: {
    failure: `deprecated kebab-case keys replaced in locale files.
To see the keys, run \`ov just frontend/run i18n --debug\`. For more details, see ${kebabCaseIssue}.`,
    success: `No deprecated kebab-case keys found in locale files. 🎉 Please close issue ${kebabCaseIssue}.`,
  },
  invalidPlaceholders: {
    failure: `invalid translation keys with extra # or empty {} symbols replaced in locale files.
To see the keys, run \`ov just frontend/run i18n --debug\`. For more details, see ${invalidPlaceholderIssue}.`,
    success: `No invalid translation keys found in locale files. 🎉 Please close issue ${invalidPlaceholderIssue}.`,
  },
}

const logWarnings = (deprecatedKeys, invalidKeys, debug) => {
  for (const [keysKind, keysObject] of [
    ["kebabCase", deprecatedKeys],
    ["invalidPlaceholders", invalidKeys],
  ]) {
    if (keysObject.count > 0) {
      console.warn(`${keysObject.count} ${warnings[keysKind].failure}`)
      if (debug) {
        console.log(prettify(keysObject.keys))
      }
    } else {
      console.log(keysObject[keysKind].success)
    }
  }
}

const extractZip = async (zipPath, debug) => {
  const zip = new AdmZip(zipPath, {})
  let count = 0

  const deprecatedKeys = { count: 0, keys: {} }
  const invalidKeys = { count: 0, keys: {} }

  const getTargetName = (fileName) => {
    const renamed = fileName.replace("meta-openverse-", "").replace(".ngx", "")
    // Fix for invalid locale slug, see https://github.com/WordPress/openverse/issues/5059
    if (renamed.includes("kir.json")) {
      return renamed.replace("kir.json", "ky.json")
    }
    return renamed
  }

  zip.getEntries().forEach((entry) => {
    if (entry.entryName.endsWith(".json")) {
      const fileName = basename(entry.entryName)
      const targetName = getTargetName(fileName)
      const targetPath = join(localesDir, targetName)

      // Extract to a temporary location first
      zip.extractEntryTo(entry, localesDir, false, true, true, targetName)

      const extractedPath = join(localesDir, targetName)
      const content = readToJson(extractedPath)

      const nonNullContent = removeNullValues(content)
      const cleanedContent = replacePlaceholders(
        nonNullContent,
        targetName,
        deprecatedKeys,
        invalidKeys
      )

      // Only save if there are translations
      if (Object.keys(cleanedContent).length > 0) {
        if (debug) {
          console.log(`Writing ${targetPath}`)
        }
        writeJson(targetPath, cleanedContent)
        count++
      } else {
        // Remove the temporary file
        unlinkSync(extractedPath)
      }
    }
  })
  logWarnings(deprecatedKeys, invalidKeys, debug)

  return count
}

/**
 * Replace ###<text>### with {<text>}.
 *
 * @param {any} json - the JSON object to replace placeholders in
 * @param {string} locale - the locale of the JSON object
 * @param {object} deprecatedKeys - object to store deprecated kebab-cased keys and number of replacements.
 * @param {object} invalidKeys - object to store invalid values that contain extra `#` or `{}`, and number of replacements.
 * @return {any} the sanitised JSON object
 */
const replacePlaceholders = (json, locale, deprecatedKeys, invalidKeys) => {
  const recordProblems = (key, problems) => {
    problems.count++
    problems.keys[locale] = [...(problems.keys[locale] ?? []), key]
  }
  /**
   * Replaces ###<text>### from `po` files with {<text>} in `vue`.
   * Additionally, the old kebab-cased keys that can still be in the
   * translations are replaced with camelCased keys the app expects.
   */
  function replacer(_, match) {
    if (match.includes("-")) {
      recordProblems(match, deprecatedKeys)
    }
    return `{${kebabToCamel(match)}}`
  }

  function cleanupString(str, key) {
    if (str.includes("||")) {
      return ""
    }
    const cleaned = str
      .replace(/[{}]/g, "###") // Replace all { and } with ###
      .replace(/<\/?em>/g, "") // Remove <em> and </em> tags

    let replaced = cleaned.replace(/###([a-zA-Z-]*?)###/g, replacer)
    // Irregular placeholders with more or fewer than 3 #s
    replaced = replaced.replace(/#{1,4}([a-zA-Z-]+?)#{1,4}/g, "{$1}")

    if (replaced.includes("{}")) {
      recordProblems(`${key}:${cleaned}`, invalidKeys)
      replaced = ""
    }
    const withoutOpenverseChannel = replaced.replace("#openverse", "")
    if (withoutOpenverseChannel.includes("#")) {
      recordProblems(`${key}:${cleaned}`, invalidKeys)
      replaced = ""
    }
    return replaced
  }

  for (const [key, value] of Object.entries(json)) {
    json[key] = cleanupString(value, key)
  }
  return json
}

/**
 * Perform a bulk download of translation strings from GlotPress and extract the
 * JSON files from the ZIP archive.
 *
 * @return {Promise<boolean>} - whether the bulk download succeeded
 */
export const downloadTranslations = async (debug) => {
  console.log("Performing bulk translations download.")
  try {
    const zipPath = await fetchBulkNgx()
    const translationsCount = await extractZip(zipPath, debug)
    unlinkSync(zipPath)
    console.log(`Successfully saved ${translationsCount} translations.`)
    return true
  } catch (error) {
    console.error("Failed to download translations:", error)
    return false
  }
}
/**
 * Convert en.json5 to en.json, and return the number of keys in the file,
 * if `countKeys` is true.
 * @param {boolean} countKeys
 * @return {number}
 */
export const writeEnglish = (countKeys = false) => {
  const enJson5 = readFileSync(enJson5File, "utf8")
  const fileContents = json5.parse(enJson5)
  writeJson(enJsonFile, fileContents)
  if (countKeys) {
    return Object.keys(fileContents).length
  }
}
