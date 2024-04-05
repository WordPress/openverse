const fs = require("fs")
const path = require("path")

const ts = require("typescript")

/**
 * @typedef {{text: string, links: {text: string, dest?: string}[]}} Comment
 * @typedef {{name: string, type: string, isOptional: boolean, documentation: Comment | undefined}} Field
 */

const preamblePath = path.resolve(__dirname, "preamble.md")
const docsFilePath = path.resolve(__dirname, "../media_properties.md")

/**
 * Generate Markdown documentation for an interface. This generates both the
 * data type table and the following long-form descriptions from the TSDoc
 * docstrings.
 *
 * @param node {ts.Node} the interface node to document
 * @param ast {ts.SourceFile} the AST for the media types file
 * @returns {string} the Markdown documentation for the interface
 */
function documentInterface(node, ast) {
  const fields = getInterfaceFields(node, ast).sort((a, b) =>
    a.name.localeCompare(b.name)
  )

  /** @type {string[]} */
  const output = []

  output.push(`## Interface \`${node.name.text}\``)

  output.push("### Fields")

  // Notes
  const notes = []
  const noted_fields = []
  for (const field of fields) {
    if (field.documentation) {
      noted_fields.push(field.name)
      notes.push(`\n(${node.name.text}-${field.name}-notes)=`)
      notes.push(`#### \`${field.name}\``)
      notes.push(field.documentation.text)
      if (field.documentation.links.length) {
        notes.push("\n**See also:**")
        for (const link of field.documentation.links) {
          notes.push(`- [${link.text}](${link.dest || link.text})`)
        }
      }
    }
  }

  // Table
  output.push("| Name | Type | Optional? |")
  output.push("|-|-|-|")

  for (const field of fields) {
    let fieldName = `\`${field.name}\``
    if (noted_fields.includes(field.name)) {
      fieldName = `[${fieldName}](#${node.name.text}-${field.name}-notes)`
    }

    let fieldType = field.type.replace("|", "\\|")
    fieldType = `\`${fieldType}\``
    if (fieldType[1] >= "A" && fieldType[1] <= "Z") {
      // hack to identify custom types
      fieldType = `${fieldType} (custom)`
    }
    if (fieldType[1] === '"' && fieldType.at(-2) === '"') {
      // hack to identify literal types
      fieldType = `${fieldType} (literal)`
    }

    const columns = [fieldName, fieldType, field.isOptional ? "✓" : ""]
    output.push(`|${columns.join("|")}|`)
  }

  // Notes
  output.push("### Notes")
  output.push(...notes)

  return output.join("\n")
}

/**
 * Determine whether the interface node is, or extends from, interface `Media`.
 *
 * @param node {ts.Node} the node to check for being, or extending from, `Media`
 * @returns {boolean} whether the node is, or extends from, interface `Media`
 */
function isOfInterest(node) {
  return (
    node.name.text === "Media" ||
    (node.heritageClauses &&
      node.heritageClauses.some((clause) =>
        clause.types.some((type) => type.expression.text === "Media")
      ))
  )
}

/**
 * Extract all the properties from the interface.
 *
 * @param node {ts.Node} the interface node to extract fields from
 * @param ast {ts.SourceFile} the AST for the media types file
 * @returns {Field[]} the fields of the interface
 */
function getInterfaceFields(node, ast) {
  return node.members.map((member) => {
    if (ts.isPropertySignature(member) && member.name) {
      const name = member.name.text
      const documentation = extractComments(member, ast)
      const type = member.type ? member.type.getText(ast) : "unknown"
      const isOptional = Boolean(member.questionToken)
      return { name, type, isOptional, documentation }
    }
  })
}

/**
 * Extracts and parses the JSDoc comment for a node.
 *
 * @param node {ts.Node} the AST node for which to get the comments
 * @param ast {ts.SourceFile}
 * @returns {Comment | undefined} the parsed docstring comment
 */
function extractComments(node, ast) {
  const fullText = node.getFullText(ast)

  let commentRanges = ts.getLeadingCommentRanges(fullText, 0)
  if (!commentRanges) {
    return undefined
  }

  const comments = commentRanges
    .filter((range) => range.kind === ts.SyntaxKind.MultiLineCommentTrivia)
    .map((range) => fullText.substring(range.pos, range.end))
    .filter((comment) => comment.startsWith("/**"))
  if (!comments.length) {
    return undefined
  }

  let links = []
  let text = comments
    .at(-1) // retain only the last doc comment
    .split("\n")
    .map((line) =>
      line
        .replace("/**", "") // remove start of docstring
        .replace("*/", "") // remove end of docstring
        .replace(/^\s*\*/, "") // remove leading asterisks
        .trim()
    )
    .filter((line) => {
      if (!line) {
        return false
      }
      if (!line.startsWith("@see")) {
        return true // keep the line as text, and move to the next line
      }

      const match = line.match(/\{@link (?<dest>[^|]*)(\|(?<text>.*))?}/)
      if (match) {
        links.push({
          dest: match.groups.dest,
          text: match.groups.text || match.groups.dest,
        })
      } else {
        links.push({ text: line.replace("@see", "").trim() })
      }
      return false // remove the line from text as it will be in links
    })
    .join("\n")

  return { text, links }
}

/**
 * Convert the file with media types and interfaces into an AST using the
 * TypeScript compiler.
 *
 * @returns {ts.SourceFile} the AST for the media types file
 */
function getAst() {
  const tsFilePath = path.resolve(__dirname, "../src/types/media.ts")
  console.log(`Parsing ${tsFilePath}.`)

  return ts.createSourceFile(
    "media.ts",
    fs.readFileSync(tsFilePath, "utf-8"),
    ts.ScriptTarget.Latest
  )
}

/**
 * Get all interfaces that are, or extend from, interface `Media` from the
 * source code.
 *
 * @param ast {ts.SourceFile} the AST to search for interfaces
 * @returns {ts.Node[]} the interface `Media` and interfaces that extend from it
 */
function getMediaInterfaces(ast) {
  /** @type {ts.Node[]} */
  const mediaInterfaces = []

  const visit = (node) => {
    if (ts.isInterfaceDeclaration(node) && isOfInterest(node)) {
      mediaInterfaces.push(node)
    }
    ts.forEachChild(node, visit)
  }
  visit(ast)

  return mediaInterfaces
}

/**
 * Write the generated documentation with preamble to the output file.
 *
 * @param docs {string} the generated documentation to write below the preamble
 */
function writeDocs(docs) {
  const preamble = fs.readFileSync(preamblePath, "utf-8")
  console.log(`Writing to ${docsFilePath}.`)
  fs.writeFileSync(docsFilePath, [preamble, docs].join("\n"))
}

/*
 **************
 * Entrypoint *
 **************
 */

function main() {
  const ast = getAst()
  const mediaInterfaces = getMediaInterfaces(ast)
  const docs = mediaInterfaces
    .map((mediaInterface) => documentInterface(mediaInterface, ast))
    .join("\n")
  writeDocs(docs)
}

main()
