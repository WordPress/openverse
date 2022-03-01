const fs = require('fs')

const json = require('../en.json')

const { createPotFile } = require('./json-pot-helpers')

const matchPotCreationDate = /^"POT-Creation-Date: .*\\n"$/gm

try {
  const fileName = process.cwd() + '/src/locales/po-files/openverse.pot'
  const existingPotFile = String(fs.readFileSync(fileName)).replace(
    matchPotCreationDate,
    ''
  )
  const potFile = createPotFile(json)

  if (existingPotFile === potFile.replace(matchPotCreationDate, '')) {
    console.log('No change detected in pot file, skipping write')
    return process.exit(0)
  }

  fs.writeFileSync(fileName, createPotFile(json))
  console.log(`Successfully wrote pot file to ${fileName}`)
} catch (err) {
  console.error(err)
}
