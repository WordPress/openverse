/**
 * Extract custom event names from the `Events` type in `frontend/src/types/analytics.ts`
 * This script is used by `setup_plausible.sh` to automatically provision
 * existing custom events.
 */
const fs = require("fs")
const path = require("path")

const ts = require("typescript")

const analyticsTypesModule = path.resolve(
  __dirname,
  "..",
  "src",
  "types",
  "analytics.ts"
)

function main() {
  const sourceFile = ts.createSourceFile(
    analyticsTypesModule,
    fs.readFileSync(analyticsTypesModule, "utf-8")
  )

  const eventsType = sourceFile.statements.find(
    (s) => s.name?.escapedText === "Events"
  )
  const eventNames = eventsType.type.members.map((m) => m.name.escapedText)

  console.log(eventNames.join(" "))
}

main()
