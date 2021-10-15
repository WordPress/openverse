const json = require('../en.json')
const fs = require('fs')
const { createPotFile } = require('./json-pot-helpers')

try {
  const fileName = process.cwd() + '/src/locales/po-files/openverse.pot'
  fs.writeFileSync(fileName, createPotFile(json))
  console.log(`Successfully wrote pot file to ${fileName}`)
} catch (err) {
  console.error(err)
}
