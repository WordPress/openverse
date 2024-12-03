/**
 This script extracts data for locales available in GlotPress and translate.wp.org,
 transforms some locale properties to match what Vue i18n expects,
 and saves it to `wp-locales-list.json`.
 Updates the translation status of locales list from wp-locales-list,
 and saves lists of translated and untranslated locales with properties expected
 by Vue i18n.
 */
import { join } from "path"
import { copyFileSync, existsSync, readdirSync } from "fs"

import { userAgentHeader } from "../../shared/constants/user-agent.mjs"

import { readToJson, snakeToCamel } from "./utils.mjs"
import { i18nDataDir, localesDir, testLocalesDir } from "./paths.mjs"

const base_url =
  "https://raw.githubusercontent.com/GlotPress/GlotPress/refs/heads/develop/locales/locales.php"

// Fix invalid locale slugs, see https://github.com/WordPress/openverse/issues/5059
const LOCALES_FIX = {
  kir: "ky",
}

// Pattern to match all locales except English (US). We don't want to overwrite `en.json`,
// which is copied from `en.json5`.
const WP_LOCALE_PATTERN = /wp_locale *= *'(?!en_US\b)([^']+)';/

const DEFAULT_LOCALE_PROPERTIES = [
  "english_name",
  "native_name",
  "slug", // unique identifier used by Nuxt i18n, used for HTML lang attribute
  "text_direction",
  "nplurals",
  "plural_expression",
]

const createPropertyRePatterns = () => {
  const propertyRePatterns = {}
  const properties = process.argv.includes("--plural")
    ? [...DEFAULT_LOCALE_PROPERTIES]
    : [...DEFAULT_LOCALE_PROPERTIES].filter(
        (prop) => !["plural_expression", "nplurals"].includes(prop)
      )
  properties.forEach((prop) => {
    propertyRePatterns[prop] =
      prop === "nplurals"
        ? new RegExp(`${prop} *= *(\\d+);`)
        : new RegExp(`${prop} *= *'(.*)';`)
  })
  return propertyRePatterns
}

const PROPERTY_PATTERNS = createPropertyRePatterns()

/**
 * Fetches the data from GlotPress GitHub.
 * @returns {Promise<string>}
 */
async function fetchLocalesPhpFile() {
  try {
    const res = await fetch(base_url, { headers: userAgentHeader })
    return await res.text()
  } catch (error) {
    console.error("Failed to fetch locales.php from GlotPress", error)
    return ""
  }
}

/**
 * Parses the raw string for each locale and extracts the properties we need.
 * Only saves the locales that are supported by https://translate.wordpress.org/
 * (that is, the locales that have a `wp_locale` property).
 *
 * @param rawData {string}
 * @return {import("./types").RawI18nLocaleProps}
 */
function parseLocaleMetadata(rawData) {
  const wpLocaleMatch = rawData.match(WP_LOCALE_PATTERN)

  if (wpLocaleMatch) {
    const data = {}

    // Extract the values, convert the property names to camelCase,
    // replace `english_name` with `name`, and remove the quotes around pluralization values.
    Object.keys(PROPERTY_PATTERNS).forEach((key) => {
      const value = rawData.match(PROPERTY_PATTERNS[key])
      if (value) {
        const propName = key === "english_name" ? "name" : snakeToCamel(key)
        if (propName === "nplurals") {
          data[propName] = Number.parseInt(value[1], 10)
        } else {
          data[propName] = value[1]
        }
      }
    })
    return /** @type import("./types").RawI18nLocaleProps */ (data)
  }
}

/**
 * Fetches locale data from the GlotPress GitHub repository.
 * Extracts properties, converts locale property names to camelCase as expected
 * by Vue i18n, and adds `code` property to each locale.
 * @returns {Promise<import("./types").RawI18nLocaleProps[]>}
 */
export async function fetchAndParseLocaleMetadata() {
  const data = await fetchLocalesPhpFile()

  // Splits the text by the new locale declaration string, and extracts locale metadata
  // from each locale record.
  const supportedLocales = data
    .split("new GP_Locale();")
    .splice(1)
    .map((item) => item.trim())
    .map(parseLocaleMetadata)
    .filter(Boolean)

  console.log(
    `${supportedLocales.length} locales available on https://translate.wordpress.org found in GlotPress repository.`
  )

  return supportedLocales
}

/**
 * Computes the `translated` percentage for a locale. If the locale json file does not
 * exist, returns 0.
 * Otherwise, counts the number of keys in the locale file, and computes the `translated`
 * percentage using the total number of keys in the original `en.json5` file.
 * @param jsonFilePath - the current locale file name.
 * @param totalKeysCount - the total number of keys in the `en.json5` file.
 * @return {number}
 */
const getTranslatedPercentage = (jsonFilePath, totalKeysCount) => {
  const fileLocation = join(localesDir, jsonFilePath)
  if (!existsSync(fileLocation)) {
    return 0
  }
  const jsonKeysCount = Object.keys(readToJson(fileLocation)).length
  return Math.ceil((jsonKeysCount * 100) / totalKeysCount)
}

/**
 * Returns a list of locale objects with at least one translated string
 * @returns {Promise<import("./types").LocalesByTranslation>}
 */
export const getWpLocalesMetadata = async (
  totalKeysCount,
  debug,
  getPluralization = false
) => {
  const localesList = await fetchAndParseLocaleMetadata()
  if (getPluralization) {
    getPluralizationRules(localesList)
  }

  const result = {
    translated: [],
    untranslated: [],
  }
  Object.values(localesList).map((locale) => {
    if (locale.slug in LOCALES_FIX) {
      const fixedSlug = LOCALES_FIX[locale.slug]
      if (debug) {
        console.log(
          `Changing invalid locale slug ${locale.slug} to ${fixedSlug}`
        )
      }
      locale.slug = fixedSlug
    }
    const localeFile = `${locale.slug}.json`

    const translated = getTranslatedPercentage(localeFile, totalKeysCount)

    const localeProperties = {
      /* Nuxt i18n fields */
      code: locale.slug,
      dir: locale.textDirection || "ltr",
      file: localeFile,
      // Used for the html lang attribute.
      language: locale.slug,

      /* Custom fields */
      name: locale.name,
      nativeName: locale.nativeName || locale.name,
      translated,
    }
    if (translated > 0) {
      result.translated.push(localeProperties)
    } else {
      result.untranslated.push(localeProperties)
    }
  })

  return result
}

/**
 * Some locales have custom pluralization rules that differ from the default
 * rules provided by Vue i18n. This function extracts the pluralization rules
 * from the locales metadata and logs them in a format that can be copied to
 * the `vue-i18n.ts` settings file.
 * There shouldn't be a need to update it often, but it's here for reference.
 * @param {import('./types').RawI18nLocaleProps[]} locales
 */
const getPluralizationRules = (locales) => {
  const rules = {}
  for (const locale of locales) {
    // For Vue, the default pluralization rules handle cases where
    // - nplurals=2 and pluralExpression="n > 1"
    // - nplurals=1 and pluralExpression="0"
    // We don't need to include these rules in the settings file.
    const isDefaultPluralization =
      (!locale.nplurals && !locale.pluralExpression) ||
      (locale.nplurals === 2 && locale.pluralExpression === "n > 1") ||
      (locale.nplurals === 1 && locale.pluralExpression === "0")
    if (!isDefaultPluralization) {
      if (locale.nplurals === 2) {
        // When nplurals is 2, the plural expression is a boolean expression.
        // Convert it to return `0` or `1`.
        const isBoolean =
          typeof eval(locale.pluralExpression.replaceAll("n", "1")) ===
          "boolean"
        if (isBoolean) {
          locale.pluralExpression = `(${locale.pluralExpression}) ? 1 : 0`
        }
      }
      rules[locale.slug] = `(n: number): number => ${locale.pluralExpression},`
    }
  }
  const pluralRulesFiles = Object.entries(rules)
    .map(([key, value]) => `${key}: ${value}`)
    .join("\n")

  console.log(pluralRulesFiles)
}

/**
 * Copies the test translation files and the corresponding `valid-locales.json`
 * file to the `i18n/locales` directory for running Playwright tests.
 * @return {Promise<void>}
 */
export async function copyTestLocalesMetadata() {
  console.log("Copying translations from the test folder...")
  const files = readdirSync(testLocalesDir)

  await Promise.all(
    files.map(async (file) => {
      const sourcePath = join(testLocalesDir, file)
      const destPath =
        file === "valid-locales.json"
          ? join(i18nDataDir, file)
          : join(localesDir, file)
      copyFileSync(sourcePath, destPath)
    })
  )
  console.log("Done copying!")
}
