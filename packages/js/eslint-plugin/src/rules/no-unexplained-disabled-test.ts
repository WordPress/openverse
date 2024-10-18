import { OpenverseRule } from "../utils/rule-creator"

import type { TSESTree } from "@typescript-eslint/utils"

type MessageIds = "missingIssueComment"

const messages = {
  missingIssueComment:
    "Disabled tests must have an issue comment with a GitHub link preceding them.",
} as const

export const noUnexplainedDisabledTest = OpenverseRule<[], MessageIds>({
  name: "no-unexplained-disabled-test",
  meta: {
    type: "problem",
    docs: {
      description:
        "Disabled tests must have an issue comment with a GitHub link preceding them.",
      recommended: true,
    },
    schema: [],
    messages,
  },
  defaultOptions: [],
  create(context) {
    const sourceCode = context.sourceCode

    const hasIssueCommentWithLink = (node: TSESTree.Node) => {
      const commentsBeforeNode = sourceCode.getCommentsBefore(node)
      for (const comment of commentsBeforeNode) {
        if (/\bhttps:\/\/github\.com\/.*?\/issues\/\d+\b/.test(comment.value)) {
          return true
        }
      }

      return false
    }

    const testSkipRegex = /^test\.skip\s*\(/g
    const testSkipEachRegex = /^test\.skip\.each\s*\(/g
    const testConcurrentSkipEachRegex = /^test\.concurrent\.skip\.each\s*\(/g
    const testTodoRegex = /^test\.todo\s*\(/g
    const itSkipRegex = /^it\.skip\s*\(/g
    const itEachSkipRegex = /^it\.each\.skip\s*\(/g
    const describeSkipRegex = /^describe\.skip\s*\(/g
    const describeEachSkipRegex = /^describe\.each\.skip\s*\(/g

    return {
      CallExpression(node) {
        const nodeText = sourceCode.getText(node)
        if (
          testSkipRegex.test(nodeText) ||
          testSkipEachRegex.test(nodeText) ||
          testConcurrentSkipEachRegex.test(nodeText) ||
          testTodoRegex.test(nodeText) ||
          itSkipRegex.test(nodeText) ||
          itEachSkipRegex.test(nodeText) ||
          describeSkipRegex.test(nodeText) ||
          describeEachSkipRegex.test(nodeText)
        ) {
          if (!hasIssueCommentWithLink(node)) {
            context.report({
              node,
              messageId: "missingIssueComment",
            })
          }
        }
      },
    }
  },
})
