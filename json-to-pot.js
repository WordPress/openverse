const json = require('./src/locales/en.json')

const curlyRegex = new RegExp('{[a-z]*}')
const containsCurlyWord = (string) => curlyRegex.test(string)
const checkStringForVars = (string) =>
  containsCurlyWord(string) ? '(Do not translate words in curly braces)' : ''

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

// POT Syntax

// msgctxt context
// msgid untranslated-string
// msgstr translated-string

function potTime(json, parent = json) {
  let potFile = ''
  for (const row of Object.entries(json)) {
    let [key, value] = row
    if (typeof value === 'string') {
      potFile = `${potFile}

# ${findPath(parent, key)}.${key} ${checkStringForVars(value)}
msgctxt "${findPath(parent, key)}.${key}"
msgid "${value}"
msgstr ""`
    }
    if (typeof value === 'object') {
      potFile = `${potFile}${potTime(value, parent)}`
    }
  }
  return potFile
}

const potFile = potTime(json)

console.log(potFile)
