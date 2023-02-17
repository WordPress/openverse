const fs = require("fs")
const path = require("path")

const { parseJson } = require("./read-i18n")
const { makePot } = require("./json-pot-helpers")

try {
  const fileName = path.resolve(process.cwd(), "openverse.pot")

  const entries = parseJson("en.json5")
  fs.writeFileSync(fileName, makePot(entries), { flag: "w" })
  console.log(`Successfully wrote pot file to ${fileName}`)
} catch (err) {
  console.error(err)
}
