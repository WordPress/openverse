module.exports = {
    rules: {
      'no-disabled-test': (context) => {
        const sourceCode = context.getSourceCode();
        const comments = sourceCode.getAllComments();
        const disabledTestRegex = /^\s*test\.(skip|todo)\(.*?\)/;
  
        const hasIssueComment = (node) => {
          const precedingComments = sourceCode.getCommentsBefore(node);
          for (const comment of precedingComments) {
            if (/issue/i.test(comment.value)) {
              return true;
            }
          }
          return false;
        };
  
        return {
          CallExpression(node) {
            if (
              disabledTestRegex.test(sourceCode.getText(node)) &&
              !hasIssueComment(node)
            ) {
              context.report({
                node,
                message: 'Disabled tests must have an issue comment preceding them.',
              });
            }
          },
        };
      },
    },
  };
  