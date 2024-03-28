// Copied from https://github.com/blakeembrey/change-case
// Case-related utility functions are vendored in because `case` package
// cannot be used in Nuxt 3 which requires ESM compatibility.

// Regexps involved with splitting words in various case formats.
const SPLIT_LOWER_UPPER_RE = /([\p{Ll}\d])(\p{Lu})/gu
const SPLIT_UPPER_UPPER_RE = /(\p{Lu})([\p{Lu}][\p{Ll}])/gu

// Regexp involved with stripping non-word characters from the result.
const DEFAULT_STRIP_REGEXP = /[^\p{L}\d]+/giu

// The replacement value for splits.
const SPLIT_REPLACE_VALUE = "$1\0$2"

/**
 * Split any cased input strings into an array of words.
 */
function split(input: string) {
  if (!input) {
    return []
  }

  let result = input.trim()

  result = result
    .replace(SPLIT_LOWER_UPPER_RE, SPLIT_REPLACE_VALUE)
    .replace(SPLIT_UPPER_UPPER_RE, SPLIT_REPLACE_VALUE)
    .replace(DEFAULT_STRIP_REGEXP, "\0")

  let start = 0
  let end = result.length

  // Trim the delimiter from around the output string.
  while (result.charAt(start) === "\0") {
    start++
  }
  if (start === end) {
    return []
  }
  while (result.charAt(end - 1) === "\0") {
    end--
  }

  return result.slice(start, end).split(/\0/g)
}

function pascalCaseTransformFactory() {
  return (word: string, index: number) => {
    const char0 = word[0]
    const initial =
      index > 0 && char0 >= "0" && char0 <= "9"
        ? "_" + char0
        : char0.toUpperCase()
    return initial + word.slice(1).toLowerCase()
  }
}

function capitalCaseTransformFactory() {
  return (word: string) =>
    `${word[0].toUpperCase()}${word.slice(1).toLowerCase()}`
}

/**
 * Convert a string to camel case (`fooBar`).
 */
export function camelCase(input: string) {
  const transform = pascalCaseTransformFactory()
  return split(input)
    .map((word, index) => {
      if (index === 0) {
        return word.toLowerCase()
      }
      return transform(word, index)
    })
    .join("")
}

/**
 * Convert a string to capital case (`Foo Bar`).
 */
export function capitalCase(input: string) {
  return split(input).map(capitalCaseTransformFactory()).join(" ")
}
