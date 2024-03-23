const { writeFile } = require("fs/promises")
const os = require("os")

/**
 * Convert a kebab-case string (`image-title`) to camel case (`imageTitle`).
 */
function kebabToCamel(input) {
  const split = input.split("-")
  if (split.length === 1) {
    return input
  }

  for (let i = 1; i < split.length; i++) {
    split[i] = split[i][0].toUpperCase() + split[i].slice(1)
  }
  return split.join("")
}

/**
 * Mutates an object at the path with the value. If the path
 * does not exist, it is created by nesting objects along the
 * path segments.
 *
 * @see {@link https://stackoverflow.com/a/20240290|Stack Overflow}
 *
 * @param {any} obj - The object to mutate.
 * @param {string} path - The dot delimited path on the object to mutate.
 * @param {unknown} value - The value to set at the path.
 */
exports.setToValue = function setValue(obj, path, value) {
  var a = path.split(".")
  var o = obj
  while (a.length - 1) {
    var n = a.shift()
    if (!(n in o)) {
      o[n] = {}
    }
    o = o[n]
  }
  o[a[0]] = value
}

/**
 * Replace ###<text>### with {<text>}.
 *
 * @param {any} json - the JSON object to replace placeholders in
 * @param {string} locale - the locale of the JSON object
 * @param {object} deprecatedKeys - object to store deprecated kebab-cased keys and number of replacements.
 * @return {any} the sanitised JSON object
 */
const replacePlaceholders = (json, locale, deprecatedKeys) => {
  if (json === null) {
    return null
  }

  /**
   * Replaces ###<text>### from `po` files with {<text>} in `vue`.
   * Additionally, the old kebab-cased keys that can still be in the
   * translations are replaced with camelCased keys the app expects.
   */
  function replacer(_, match) {
    if (match.includes("-")) {
      deprecatedKeys.count++
      deprecatedKeys.keys[locale] = [
        ...(deprecatedKeys.keys[locale] ?? []),
        match,
      ]
    }
    return `{${kebabToCamel(match)}}`
  }

  if (typeof json === "string") {
    return json.replace(/###([a-zA-Z-]*)###/g, replacer)
  }
  let currentJson = { ...json }

  for (const row of Object.entries(currentJson)) {
    let [key, value] = row
    currentJson[key] = replacePlaceholders(value, locale, deprecatedKeys)
  }
  return currentJson
}

exports.replacePlaceholders = replacePlaceholders

/**
 * Write translation strings to a file in the locale directory
 * @param {string} locale
 * @param {any} rawTranslations
 * @param {object} deprecatedKeys - object to store deprecated kebab-cased keys and number of replacements.
 */
exports.writeLocaleFile = (locale, rawTranslations, deprecatedKeys) => {
  const translations = replacePlaceholders(
    rawTranslations,
    locale,
    deprecatedKeys
  )

  return writeFile(
    process.cwd() + `/src/locales/${locale}.json`,
    JSON.stringify(translations, null, 2) + os.EOL
  )
}
