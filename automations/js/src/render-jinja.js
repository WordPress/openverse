const fs = require("fs")
const path = require("path")

const nunjucks = require("nunjucks")

const rootDir = path.join(__dirname, "..", "..", "..")
nunjucks.configure(rootDir, {
  trimBlocks: true,
  lstripBlocks: true,
  autoescape: true,
})

function render(inFileName, outFile, context = {}) {
  const inFilePath = path.join(rootDir, inFileName)
  const outFilePath = path.join(rootDir, outFile)
  fs.writeFileSync(
    outFilePath,
    nunjucks.renderString(fs.readFileSync(inFilePath).toString(), context)
  )
}

render(process.argv[2], process.argv[3], JSON.parse(process.argv[4]))
