const fs = require("fs")

const { parse, stringify } = require("comment-json")

let component_name = process.argv[2]

if (component_name === undefined)
  throw new Error("please provide component name")

let tsconfig = parse(fs.readFileSync("./tsconfig.json", "utf8"))

tsconfig.include.push(`src/components/${component_name}/${component_name}.vue`)
fs.writeFileSync("./tsconfig.json", stringify(tsconfig, null, 2), { flag: "w" })

console.log(`added component ${component_name} to tsconfig.json`)
