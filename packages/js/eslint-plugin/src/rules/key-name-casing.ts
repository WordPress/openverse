import { SourceCode } from "eslint"
import { JSONProperty } from "jsonc-eslint-parser/lib/parser/ast"

import { OpenverseRule } from "../utils/rule-creator"

export type CasingKind = "camelCaseWithDot" | "snake_case_with_dot"

export const allowedCaseOptions: CasingKind[] = [
  "camelCaseWithDot",
  "snake_case_with_dot",
]

const checkersMap = {
  camelCaseWithDot: isCamelCase,
  snake_case_with_dot: isSnakeCase,
}

/**
 * Checks whether the given string has symbols.
 */
function hasSymbols(str: string) {
  return /[\u0021-\u0023\u0025-\u002c./\u003a-\u0040\u005b-\u005e`\u007b-\u007d]/u.test(
    str
  ) // without " ", "$", "-" and "_"
}
/**
 * Checks whether the given string has upper.
 */
function hasUpper(str: string) {
  return /[A-Z]/u.test(str)
}
/**
 * Checks whether the given string is camelCase.
 */
export function isCamelCase(str: string): boolean {
  return !(hasSymbols(str) || /^[A-Z]/u.test(str) || /[\s\-_]/u.test(str))
}

/**
 * Checks whether the given string is snake_case.
 */
export function isSnakeCase(str: string): boolean {
  return !(hasUpper(str) || hasSymbols(str) || /-|__|\s/u.test(str))
}

/**
 * Return case checker ('camelCaseWithDot', 'snake_case_with_dot')
 */
export function getChecker(name: "camelCaseWithDot"): (str: string) => boolean {
  return checkersMap[name]
}

type Option = {
  [key in CasingKind]?: boolean
} & {
  ignores?: string[]
}

type MessageIds = "incorrectKeyNameComment"

const messages = {
  incorrectKeyNameComment:
    "Property name `{{name}}` must match one of the following formats: {{formats}}",
} as const

export const keyNameCasing = OpenverseRule<Option[], MessageIds>({
  name: "key-name-casing",
  meta: {
    docs: {
      description: "enforce naming convention to property key names",
    },
    schema: [
      {
        type: "object",
        properties: {
          camelCaseWithDot: {
            type: "boolean",
            default: true,
          },
          snake_case_with_dot: {
            type: "boolean",
            default: true,
          },
          ignores: {
            type: "array",
            items: {
              type: "string",
            },
            uniqueItems: true,
            additionalItems: false,
          },
        },
        additionalProperties: false,
      },
    ],
    messages,
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
    const option: Option = { ...context.options[0] }
    if (option.camelCaseWithDot !== false) {
      option.camelCaseWithDot = true
    }
    const ignores = option.ignores
      ? option.ignores.map((ignore) => new RegExp(ignore))
      : []
    const formats = Object.keys(option)
      .filter((key): key is "camelCaseWithDot" =>
        allowedCaseOptions.includes(key as "camelCaseWithDot")
      )
      .filter((key) => option[key])

    const checkers: ((str: string) => boolean)[] = formats.map(getChecker)

    /**
     * Check whether a given name is a valid.
     */
    function isValid(name: string): boolean {
      if (ignores.some((regex) => regex.test(name))) {
        return true
      }
      if (!checkers.length) {
        return true
      }
      if (name.includes(".")) {
        const parts = name.split(".")
        return parts.every((part) => checkers.some((c) => c(part)))
      }
      return checkers.length ? checkers.some((c) => c(name)) : true
    }

    return {
      JSONProperty(node: JSONProperty) {
        const name =
          node.key.type === "JSONLiteral" && typeof node.key.value === "string"
            ? node.key.value
            : sourceCode.text.slice(...node.key.range)
        if (!isValid(name)) {
          context.report({
            loc: node.key.loc,
            messageId: "incorrectKeyNameComment",
            data: {
              name,
              formats: formats.join(", "),
            },
          })
        }
      },
    }
  },
})
