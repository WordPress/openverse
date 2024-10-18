import { ESLintUtils } from "@typescript-eslint/utils"

export interface OpenverseDocs {
  description: string
  recommended?: boolean
  requiresTypeChecking?: boolean
}

export const OpenverseRule = ESLintUtils.RuleCreator<OpenverseDocs>(
  (ruleName) =>
    `https://docs.openverse.org/packages/js/eslint_plugin/${ruleName.replaceAll(
      "-",
      "_"
    )}.html`
)
