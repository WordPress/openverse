// More about the structure of .po files:
// https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html#PO-Files

/*
 * white-space
 #  translator-comments
 #. extracted-comments
 #: reference…
 #, flag…
 #| msgid previous-untranslated-string
 msgid untranslated-string
 msgstr translated-string
 */
const { getAllPaths, getKeyValue } = require('./json-helpers')
const { getParsedVueFiles } = require('./parse-vue-files')
const json = require('../en.json')
const fs = require('fs')

const curlyRegex = new RegExp('{[a-zA-Z-]*}')
const containsCurlyWord = (string) => curlyRegex.test(string)
const checkStringForVars = (string) =>
  containsCurlyWord(string) ? 'Do not translate words between ### ###.' : ''

/**
 * For GlotPress to display warning when the translators try to
 * replace placeholders with something else, we need to wrap the
 * placeholders with `###WORD###`
 * @param string
 * @return {string}
 */
const replaceVarsPlaceholders = (string) => {
  if (!containsCurlyWord(string)) {
    return string
  }
  const variable = /{(?<variable>[a-zA-Z-]*)}/g
  return string.replace(variable, `###$<variable>###`)
}

/**
 * Replace placeholder format for variables,
 * escape quotes (in a different PR)
 * @param string
 * @return {string}
 */
const processValue = (string) => {
  return escapeQuotes(replaceVarsPlaceholders(string))
}

const PARSED_VUE_FILES = getParsedVueFiles('**/*.?(js|vue)')

/**
 * Returns the comment with a reference github link to the line where the
 * string is used, if available. Example:
 * #: /components/HeroSection.vue:L6
 * @param {string} keyPath (eg."hero.title")
 * @return {string}
 */
const getRefComment = (keyPath) => {
  const keyValue = PARSED_VUE_FILES.find((k) => k.path === keyPath)
  return keyValue ? `\n#: ${keyValue.file}:${keyValue.line}` : ''
}

const escapeQuotes = (str) => str.replace(/"/g, '\\"')
const pluralizedKeys = [
  'all-result-count',
  'audio-result-count',
  'image-result-count',
  'all-result-count-more',
  'audio-result-count-more',
  'image-result-count-more',
]

const pot_creation_date = () => {
  const today = new Date()
  return `${today.toISOString().split('.')[0]}+00:00`
}

const POT_FILE_META = `# Copyright (C) 2021
# This file is distributed under the same license as Openverse.
msgid ""
msgstr ""
"Project-Id-Version: Openverse \\n"
"Report-Msgid-Bugs-To: https://github.com/wordpress/openverse/issues \\n"
"POT-Creation-Date: ${pot_creation_date()}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"PO-Revision-Date: 2021-MO-DA HO:MI+ZONE\\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\\n"
"Language-Team: LANGUAGE <LL@li.org>\\n"
`

// POT Syntax

// msgctxt context
// msgid untranslated-string
// msgstr translated-string

function potTime(json) {
  let potFileString = ''
  const jsonKeys = getAllPaths(json)
  jsonKeys.forEach((key) => {
    const parts = key.split('.')
    const keyName = parts[parts.length - 1]
    const value = getKeyValue(key, json)
    if (!pluralizedKeys.includes(keyName)) {
      potFileString = `${potFileString}
${
  checkStringForVars(value) ? `\n#. ${checkStringForVars(value)}` : ''
}${getRefComment(key)}
msgctxt "${key}"
msgid "${processValue(value)}"
msgstr ""`
    } else {
      const pluralizedValues = value.split('|')
      if (pluralizedValues.length === 1) {
        pluralizedValues.push(pluralizedValues[0])
      }
      potFileString = `${potFileString}
${
  checkStringForVars(value) ? `\n#. ${checkStringForVars(value)}` : ''
}${getRefComment(key)}
msgctxt "${key}"
msgid "${processValue(pluralizedValues[0])}"
msgid_plural "${processValue(pluralizedValues[1])}"
msgstr[0] ""
msgstr[1] ""`
    }
  })
  return potFileString
}

const potFile = `${POT_FILE_META}${potTime(json)}\n`
try {
  const fileName = process.cwd() + '/src/locales/po-files/openverse.pot'
  fs.writeFileSync(fileName, potFile)
  console.log(`Successfully wrote pot file to ${fileName}`)
} catch (err) {
  console.error(err)
}
module.exports = { replaceVarsPlaceholders, potTime }
