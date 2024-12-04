/**
 * More about the structure of .po files:
 * // https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html#PO-Files
 *
 * ```po
 * white-space
 * #  translator-comments
 * #. extracted-comments
 * #: reference…
 * #, flag…
 * #| msgid previous-untranslated-string
 * msgid untranslated-string
 * msgstr translated-string
 * ```
 */
import { getParsedVueFiles } from "./parse-vue-files.mjs"

const PARSED_VUE_FILES = getParsedVueFiles()

/** @param str {string} */
const escapeQuotes = (str) => str.replace(/"/g, '\\"')

/** @param str {string} */
const containsCurlyWord = (str) => /\{[a-zA-Z-]*}/.test(str)

/** @param str {string} */
const checkStringForVars = (str) =>
  containsCurlyWord(str) ? "#. Do not translate words between ### ###." : ""

/**
 * For GlotPress to display warning when the translators miss the placeholders
 * or try replacing them with something else, we need to surround the
 * placeholders with `###`.
 *
 * @param str {string} the translation string
 * @return {string} the translation string with all placeholders marked
 */
const replaceVarsPlaceholders = (str) => {
  if (!containsCurlyWord(str)) {
    return str
  }

  const variable = /\{(?<variable>[a-zA-Z-]*)}/g
  return str.replace(variable, `###$<variable>###`)
}

/**
 * Replace placeholder format for variables and escape quotes.
 *
 * @param str {string} the translation string
 * @return {string} the translation string with quotes escaped and placeholders marked
 */
const processValue = (str) => escapeQuotes(replaceVarsPlaceholders(str))

/**
 * Returns a comment with all reference to the file and line where the string is
 * used. These are prefixed with `#:`.
 *
 * @param  keyPath {string} the lineage of the entry to search in Vue files
 * @return {string[]} the list of reference comments
 */
const getRefComments = (keyPath) =>
  PARSED_VUE_FILES.filter((k) => k.path === keyPath).map(
    (item) => `#: ${item.file}:${item.line}`
  )

/**
 * Generate the comment for the POT entry. This includes any comment written on
 * the JSON entry, a message about `###` and finally references to where that
 * entry is used in the codebase.
 *
 * @return {string} the comment lines
 */
export const createComment = (key, comment, val) => {
  const res = []

  // comments given by the programmer, directed at the translator (#.)
  if (comment) {
    res.push(`#. ${comment}`)
  }

  // comments given by the programmer, directed at the translator (#.)
  const vars = checkStringForVars(val)
  if (vars) {
    res.push(vars)
  }

  // comments containing references to the program’s source code (#:)
  const refComments = getRefComments(key)
  if (refComments.length) {
    res.push(...refComments)
  }

  return res.map((item) => `${item}`).join("\n")
}

const generatePluralizationLines = (value) => {
  const pluralizedValues = value.split("|")
  if (pluralizedValues.length === 1) {
    return pluralizedValues
  }
  return [
    `msgid "${processValue(pluralizedValues[0])}"`,
    `msgid_plural "${processValue(pluralizedValues[1])}"`,
    'msgstr[0] ""',
    'msgstr[1] ""',
  ]
}
/**
 * Convert a JSON entry into a string for the POT file. This includes the
 * message context, the message id and the message string (with pluralization
 * if needed).
 *
 * @param entry {import("./types").JsonEntry} the JSON entry to convert
 * @return {string} the POT equivalent of the JSON entry
 */
export const jsonEntryToPot = ({ key, value, doc }) => {
  const poEntry = []
  if (doc) {
    poEntry.push(doc)
  }
  poEntry.push(`msgctxt "${key}"`)
  if (value.includes("|") && /(count|time)/i.test(value)) {
    poEntry.push(...generatePluralizationLines(value))
  } else {
    poEntry.push(`msgid "${processValue(value)}"`, 'msgstr ""')
  }
  return poEntry.join("\n")
}

/**
 * Parse a single or multi-line comment. If the comment is multi-line, newlines
 * and asterisks will be removed from the output.
 *
 * @param commentNode {import('@babel/types').CommentLine|import('@babel/types').CommentBlock}
 * @return {string} the text content of the comment
 */
export const parseComment = (commentNode) => {
  switch (commentNode.type) {
    case "CommentLine": {
      return commentNode.value.trim()
    }
    case "CommentBlock": {
      return commentNode.value
        .replace(/\n|\*+/g, "")
        .replace(/\s+/g, " ")
        .replace('"', '\\"')
        .trim()
    }
  }
}

/**
 * Convert a JSON entry into a object with key, value and the linked doc comment.
 * @param node {import('@babel/types').ObjectProperty | import('@babel/types').ObjectMethod | import('@babel/types').SpreadElement }
 * @return {import("./types").JsonEntry}
 */
export const nodeToEntry = (node) => {
  let key
  switch (node.key.type) {
    case "StringLiteral": {
      key = node.key.value
      break
    }
    case "Identifier": {
      key = node.key.name
      break
    }
  }
  if (!key || typeof key !== "string") {
    throw new Error(`Invalid key ${key} in node ${node.toString()}`)
  }
  const value = node.value.value ?? ""
  const parsedComment = node.leadingComments?.map(parseComment).join("")

  return { key, value, doc: createComment(key, parsedComment, value) }
}
