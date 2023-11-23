import { Rule } from "eslint"
import { TSESTree } from "@typescript-eslint/types"

type MessageIds = "missingBraces"

const messages = {
  missingBraces: "Braces are required for one-line statements.",
} as const

export const noSingleLineBrace: Rule.RuleModule<MessageIds, []> = {
  meta: {
    type: "problem",
    docs: {
      description: "Enforce braces for one-line statements",
      recommended: "error",
    },
    messages,
    schema: [],
  },
  create(context) {
    return {
      IfStatement(node: TSESTree.IfStatement): void {
        if (node.alternate && node.consequent.type !== "BlockStatement") {
          // One-line if without braces
          context.report({
            node: node.consequent,
            messageId: "missingBraces",
          })
        }
      },
      SwitchCase(node: TSESTree.SwitchCase): void {
        if (node.consequent.length === 1 && node.consequent[0].type !== "BlockStatement") {
          // One-line case without braces
          context.report({
            node: node.consequent[0],
            messageId: "missingBraces",
          })
        }
      },
    }
  },
}
