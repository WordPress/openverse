import { readFileSync, writeFileSync } from "fs"
import { join } from "path"
import { pathToFileURL } from "url"

import { parseExpression } from "@babel/parser"

import { baseDir, enJson5 } from "./paths.mjs"
import { jsonEntryToPot, nodeToEntry } from "./po/po-helpers.mjs"

const pot_creation_date = () =>
  `${new Date().toISOString().split(".")[0]}+00:00`

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

const convertJsonToPot = () => {
  try {
    const jsonContent = readFileSync(enJson5, "utf-8")
    const expression = /** @type {import("@babel/types").ObjectExpression} */ (
      parseExpression(jsonContent)
    )

    const potContent = expression.properties
      .map((child) => nodeToEntry(child))
      .map((entry) => jsonEntryToPot(entry))
      .join("\n\n")

    const potFile = join(baseDir, "openverse.pot")
    writeFileSync(potFile, POT_FILE_META + potContent)
    console.log(`Successfully wrote pot file to ${pathToFileURL(potFile)}`)
  } catch (err) {
    console.error(err)
  }
}

convertJsonToPot()
