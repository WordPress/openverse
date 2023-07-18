module.exports = {
  meta: {
    type: "problem",
    docs: {
      description:
        "Disabled tests must have an issue comment with a GitHub link preceding them",
      category: "Best Practices",
      recommended: true,
    },
    fixable: null,
    schema: [],
    messages: {
      missingIssueComment:
        "Disabled tests must have an issue comment with a GitHub link preceding them.",
    },
  },
  create: (context) => {
    const sourceCode = context.getSourceCode()
    const disabledTestRegex =
      /^\s*(?:(?:describe|test|it)\.(?:skip|todo|each|concurrent\.(?:skip|each))|test\.skip\(|describe\.skip\(|test\.concurrent\.skip\(|test\.concurrent\.each\(|test\.each\.skip\(|test\.skip\.each\(|test\.skip\.\s*`)/gm

    const hasIssueCommentWithLink = (node) => {
      const precedingComments = sourceCode.getCommentsBefore(node)
      for (const comment of precedingComments) {
        if (/\bhttps:\/\/github\.com\/.*?\/issues\/\d+\b/.test(comment.value)) {
          return true
        }
      }
      return false
    }

    return {
      CallExpression(node) {
        const nodeText = sourceCode.getText(node)
        if (
          disabledTestRegex.test(nodeText) &&
          !hasIssueCommentWithLink(node)
        ) {
          context.report({
            node,
            messageId: "missingIssueComment",
          })
        }
      },
    }
  },
}
