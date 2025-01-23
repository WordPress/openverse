import { readFileSync, writeFileSync } from "fs"
import { EOL } from "os"

export const snakeToCamel = (str) =>
  str
    .toLowerCase()
    .replace(/([-_][a-z])/g, (group) =>
      group.toUpperCase().replace("-", "").replace("_", "")
    )

/**
 * Convert a kebab-case string (`image-title`) to camel case (`imageTitle`).
 */
export function kebabToCamel(input) {
  if (!input || typeof input !== "string") {
    return ""
  }
  if (input === "-") {
    return input
  }
  const split = input.split("-")
  if (split.length === 1) {
    return input
  }

  for (let i = 1; i < split.length; i++) {
    split[i] = split[i][0].toUpperCase() + split[i].slice(1)
  }
  return split.join("")
}

export const prettify = (json) => JSON.stringify(json, null, 2)

/**
 * Write JSON data to a file with consistent formatting.
 */
export const writeJson = (fileName, data) => {
  writeFileSync(fileName, prettify(data) + EOL, {
    encoding: "utf-8",
    flag: "w+",
  })
}

export const readToJson = (filePath) => {
  return JSON.parse(readFileSync(filePath, "utf-8"))
}
