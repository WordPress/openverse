const fs = require('fs')
const path = require('path')

const json = require('../en.json')

const { createPotFile } = require('./json-pot-helpers')

try {
  const fileName = path.resolve(process.cwd(), 'openverse.pot')

  fs.writeFileSync(fileName, createPotFile(json), { flag: 'w' })
  console.log(`Successfully wrote pot file to ${fileName}`)
} catch (err) {
  console.error(err)
}
