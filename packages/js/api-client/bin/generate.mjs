import fs from "node:fs"
import path from "node:path"

import openapiTS, { astToString } from "openapi-typescript"

const ast = await openapiTS(new URL("https://api.openverse.org/v1/schema/"))
const contents = astToString(ast)
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

const out = path.resolve(
  import.meta.dirname,
  "..",
  "src",
  "generated",
  "openverse.d.ts"
)
fs.writeFileSync(out, contents)
