import { OpenverseRule } from "../utils/rule-creator"

import type { AST } from "jsonc-eslint-parser"
import type { TSESTree } from "@typescript-eslint/utils"

type Options = readonly [
  {
    maxLength: number
  },
]

const messages = {
  maxLengthExceeded:
    "The maximum translated string length is {{ maxLength }} words. Please split this string into multiple smaller strings, and add a translator comment on each indicating their relationship to one another. Avoid splitting sentences if possible, and prefer a greater number of smaller strings over a set of strings that are linguistically complex to combine.",
}

type MessageIds = keyof typeof messages

export const translationStrings = OpenverseRule<Options, MessageIds>({
  name: "translation-strings",
  meta: {
    docs: {
      description:
        "Prevent translation strings difficult for translators to handle",
      recommended: true,
    },
    type: "problem",
    messages,
    schema: [
      {
        type: "object",
        properties: {
          maxLength: {
            type: "integer",
          },
        },
        additionalProperties: false,
      },
    ],
  },
  defaultOptions: [{ maxLength: 40 }],
  create(context, [options]) {
    return {
      "JSONProperty[value.type='JSONLiteral']"(node: AST.JSONProperty): void {
        const isEnJson5 = context.filename.endsWith("en.json5")
        if (!isEnJson5) {
          return
        }

        if (node.value.type !== "JSONLiteral") {
          return
        }

        if (typeof node.value.value !== "string") {
          return
        }

        /**
         * This is an _extremely_ naive way to count the number of words in a string,
         * but we don't need to be precise here. Chances are, edge cases (like hyphenation)
         * will either only constitute a few extra words (which is within tolerance) or will
         * be in a sentence complex enough that it will exceed the naive counting anyway.
         */
        if (node.value.value.split(" ").length > options.maxLength) {
          context.report({
            messageId: "maxLengthExceeded",
            data: {
              maxLength: options.maxLength,
            },
            node: node.value as unknown as TSESTree.Node,
          })
        }
      },
    }
  },
})
