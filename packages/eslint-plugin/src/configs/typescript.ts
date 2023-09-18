import type { TSESLint } from "@typescript-eslint/utils"

export = {
  parserOptions: {
    parser: "@typescript-eslint/parser",
  },
  plugins: ["@typescript-eslint", "tsdoc"],
  extends: ["plugin:@typescript-eslint/recommended"],
  rules: {
    "@typescript-eslint/no-var-requires": ["off"],
  },
  overrides: [
    {
      files: ["*.ts"],
      rules: {
        "tsdoc/syntax": "error",
        // This rule is disabled above to avoid forcing ESM syntax on regular JS files
        // that aren't ready for it yet. We do want to enforce this for TypeScript,
        // however, so we re-enable it here.
        "@typescript-eslint/no-var-requires": ["error"],
      },
    },
  ],
} satisfies TSESLint.Linter.Config
