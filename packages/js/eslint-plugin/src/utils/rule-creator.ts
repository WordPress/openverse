import { ESLintUtils } from "@typescript-eslint/utils"

export const OpenverseRule = ESLintUtils.RuleCreator(
  (ruleName) =>
    `https://docs.openverse.org/packages/js/eslint_plugin/${ruleName.replaceAll(
      "-",
      "_"
    )}.html`
)
