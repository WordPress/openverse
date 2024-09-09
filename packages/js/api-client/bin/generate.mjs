import fs from "node:fs"
import path from "node:path"

import openapiTS, { astToString } from "openapi-typescript"

import * as prettier from "prettier"
import { ESLint } from "eslint"

const ast = await openapiTS(new URL("https://api.openverse.org/v1/schema/"))
const cleanedContents = astToString(ast)
  // This tag doesn't exist in TSDoc
  .replace(/@description/g, "")
  // Escape `>`
  .replace(/ > /g, " \\> ")
  // Rewrite double back-tick to single back-tick
  .replace(/``/g, "`")
  // The `@enum` tag does not exist in TSDoc
  .replace(/@enum \{string\}/g, "")
  // Some of the replacements above result in empty comments, which can be removed
  .replace(/(?<=\n\s*)\/\*\*[*\s]+?\*\/\n/g, "")
  // Escape curly braces that aren't the start of TSDoc tags to avoid parser confusion
  .replace(/\*.+?[{}]\n/g, (substring) =>
    substring.replace(/\{/, "\\{").replace(/\}/, "\\}")
  )

const prettierConfig = await prettier.resolveConfig(import.meta.url)

if (!prettierConfig) {
  throw new Error(
    "Unable to resolve Prettier configuration location for `@openverse/api-client` type generation.",
    import.meta.url
  )
}

const formattedContents = await prettier.format(cleanedContents, {
  ...prettierConfig,
  parser: "typescript",
})

const eslint = new ESLint({ fix: true })

// Supply a filePath so ESLint can guess which linters to apply
const [{ output }] = await eslint.lintText(formattedContents, {
  filePath: "openverse.d.ts",
})

// output is only defined if changes were made
const lintedContents = output || formattedContents

const out = path.resolve(
  import.meta.dirname,
  "..",
  "src",
  "generated",
  "openverse.ts"
)
fs.writeFileSync(out, lintedContents)
