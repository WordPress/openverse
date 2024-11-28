import { SourceCode } from "eslint"
import { JSONProperty } from "jsonc-eslint-parser/lib/parser/ast"

import { OpenverseRule } from "../utils/rule-creator"

type CaseFormat = "camelCaseWithDot" | "snake_case_with_dot"

/**
 * Validates if a string matches the specified case format
 */
function isValidCase(str: string, format: CaseFormat): boolean {
  const patterns = {
    camelCaseWithDot: /^[a-z][a-zA-Z0-9]*$/,
    snake_case_with_dot: /^[a-z0-9]+(_[a-z0-9]+)*$/,
  }

  if (str.includes(".")) {
    return str.split(".").every((part) => {
      if (/^\d+$/.test(part)) {
        return true
      }
      return patterns[format].test(part)
    })
  }
  return patterns[format].test(str)
}

type RuleOptions = {
  camelCaseWithDot?: boolean
  snake_case_with_dot?: boolean
  ignores?: string[]
}

export const keyNameCasing = OpenverseRule<
  [RuleOptions],
  "incorrectKeyNameComment"
>({
  name: "key-name-casing",
  meta: {
    docs: {
      description: "enforce naming convention to property key names",
    },
    schema: [
      {
        type: "object",
        properties: {
          camelCaseWithDot: { type: "boolean", default: true },
          snake_case_with_dot: { type: "boolean", default: true },
          ignores: {
            type: "array",
            items: { type: "string" },
            uniqueItems: true,
          },
        },
        additionalProperties: false,
      },
    ],
    messages: {
      incorrectKeyNameComment:
        "Property name `{{name}}` must match one of the following formats: {{formats}}",
    },
    type: "suggestion",
  },
  defaultOptions: [
    {
      camelCaseWithDot: true,
      snake_case_with_dot: true,
    },
  ],
  create(context) {
    const sourceCode = context.sourceCode
    if (!(sourceCode.parserServices as SourceCode.ParserServices).isJSON) {
      return {}
    }

    const options = { ...context.options[0] }
    const ignores = options.ignores?.map((pattern) => new RegExp(pattern)) || []
    const enabledFormats = (
      ["camelCaseWithDot", "snake_case_with_dot"] as const
    ).filter((format) => options[format] !== false)

    function isValidName(name: string): boolean {
      if (!enabledFormats.length || ignores.some((regex) => regex.test(name))) {
        return true
      }

      return enabledFormats.some((format) => isValidCase(name, format))
    }

    return {
      JSONProperty(node: JSONProperty) {
        const name =
          node.key.type === "JSONLiteral" && typeof node.key.value === "string"
            ? node.key.value
            : sourceCode.text.slice(...node.key.range)

        if (!isValidName(name)) {
          context.report({
            loc: node.key.loc,
            messageId: "incorrectKeyNameComment",
            data: {
              name,
              formats: enabledFormats.join(", "),
            },
          })
        }
      },
    }
  },
})
