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
const getParsedVueFiles = require('./parse-vue-files.js')
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
  let result = ''
  const variable = /{(?<variable>[a-zA-Z-]*)}/g
  result = string.replace(variable, (match) => match.toUpperCase())
  result = result.replace(variable, `###$<variable>###`)
  return result
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

const findPath = (ob, key) => {
  const path = []
  const keyExists = (obj) => {
    if (!obj || (typeof obj !== 'object' && !Array.isArray(obj))) {
      return false
    } else if (key in obj) {
      return true
    } else if (Array.isArray(obj)) {
      let parentKey = path.length ? path.pop() : ''

      for (let i = 0; i < obj.length; i++) {
        path.push(`${parentKey}[${i}]`)
        const result = keyExists(obj[i], key)
        if (result) {
          return result
        }
        path.pop()
      }
    } else {
      for (const k in obj) {
        path.push(k)
        const result = keyExists(obj[k], key)
        if (result) {
          return result
        }
        path.pop()
      }
    }
    return false
  }

  keyExists(ob)

  return path.join('.')
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

function potTime(json, parent = json) {
  let potFile = ''
  for (const row of Object.entries(json)) {
    let [key, value] = row
    if (typeof value === 'string') {
      const keyPath = `${findPath(parent, key)}.${key}`
      if (pluralizedKeys.includes(key)) {
        const pluralizedValues = value.split('|')
        if (pluralizedValues.length === 1) {
          pluralizedValues.push(pluralizedValues[0])
        }
        potFile = `${potFile}
${
  checkStringForVars(value) ? `\n#. ${checkStringForVars(value)}` : ''
}${getRefComment(keyPath)}
msgctxt "${keyPath}"
msgid "${processValue(pluralizedValues[0])}"
msgid_plural "${processValue(pluralizedValues[1])}"
msgstr[0] ""
msgstr[1] ""`
      } else {
        potFile = `${potFile}
${
  checkStringForVars(value) ? `\n#. ${checkStringForVars(value)}` : ''
}${getRefComment(keyPath)}
msgctxt "${keyPath}"
msgid "${processValue(value)}"
msgstr ""`
      }
    }
    if (typeof value === 'object') {
      potFile = `${potFile}${potTime(value, parent)}`
    }
  }
  return potFile
}

const potFile = `${POT_FILE_META}${potTime(json)}\n`
try {
  const fileName = process.cwd() + '/src/locales/po-files/openverse.pot'
  fs.writeFileSync(fileName, potFile)
  console.log(`Successfully wrote pot file to ${fileName}`)
} catch (err) {
  console.error(err)
}
