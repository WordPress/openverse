import { join } from "path"
import { existsSync, mkdirSync, writeFileSync } from "fs"
import { pathToFileURL } from "url"

import { watch } from "chokidar"

import { prettify, writeJson } from "./utils.mjs"
import { downloadTranslations, writeEnglish } from "./translations.mjs"
import {
  enJson5 as enJson5File,
  i18nDataDir,
  localesDir,
  validLocales,
} from "./paths.mjs"
import { copyTestLocalesMetadata, getWpLocalesMetadata } from "./metadata.mjs"

/**
 * Sets up the data for i18n in Openverse:
 * - Copies en.json5 to en.json
 * - Downloads translations from GlotPress if necessary
 * - Generates locales metadata for Vue i18n for the locales with translations
 * - For tests, copies the existing metadata from the test `locales` directory.
 * - For development, watches the `en.json5` file for changes and updates `en.json` accordingly.
 * @param options
 * @return {Promise<void>}
 */
const setupI18n = async (options) => {
  console.log("Setting up i18n")

  if (!existsSync(localesDir)) {
    console.log("Creating locales directory...")
    mkdirSync(localesDir)
  }

  // Count the number of English strings to calculate translated percentage later
  let totalKeysCount = 0

  // Copy en.json5 to en.json
  try {
    totalKeysCount = writeEnglish(true)
    console.log("Copied en.json5 to en.json")
  } catch (error) {
    console.error("Failed to copy en.json5 to en.json:", error)
    process.exit(1)
  }

  if (options.enOnly) {
    writeJson(validLocales, [])
    return
  }

  if (options.test) {
    await copyTestLocalesMetadata()
    return
  }
  if (options.noGet) {
    console.log("Skipping download, re-using existing translation files.")
  } else {
    console.log("Getting translations...")
    const success = await downloadTranslations(!!options.verbose)
    if (!success) {
      process.exit(1)
    }
  }
  console.log("Starting locale metadata generation...")
  const localesMetadata = await getWpLocalesMetadata(
    totalKeysCount,
    options.verbose,
    options.getPluralizations
  )
  const files = {
    translated: {
      path: validLocales,
      data: localesMetadata.translated,
      count: localesMetadata.translated.length,
    },
    untranslated: {
      path: join(i18nDataDir, "untranslated-locales.json"),
      data: localesMetadata.untranslated,
      count: localesMetadata.untranslated.length,
    },
  }
  for (const [type, { path, data, count }] of Object.entries(files)) {
    writeFileSync(path, prettify(data))
    console.log(
      `Wrote metadata for ${count} ${type} locales to ${pathToFileURL(path)}.`
    )
  }
}

const options = {
  enOnly: process.argv.includes("--en-only"),
  watch: process.argv.includes("--watch"),
  noGet: process.argv.includes("--no-get"),
  requireComplete: process.argv.includes("--require-complete"),
  verbose: process.argv.includes("--debug"),
  test: process.argv.includes("--test"),
  getPlurals: process.argv.includes("--plural"),
}

setupI18n(options)
  .then(() => {
    console.log("i18n setup complete.")
    if (options.watch) {
      console.log("Watching en.json5 for changes...")
      watch(enJson5File).on("all", (event, path) => {
        console.log(`Event '${event}' for file ${path}`)
        writeEnglish()
      })
    }
  })
  .catch((error) => {
    console.error("i18n setup failed:", error)
    if (options.requireComplete) process.exitCode = 1
  })
