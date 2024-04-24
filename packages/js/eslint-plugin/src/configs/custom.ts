import type { TSESLint } from "@typescript-eslint/utils"

/**
 * ESLint rules created by and for the Openverse project.
 */
export = {
  plugins: ["@openverse"],
  rules: {
    "@openverse/analytics-configuration": [
      "error",
      {
        reservedPropNames: ["width", "height"],
      },
    ],
    "@openverse/no-unexplained-disabled-test": ["error"],
    "@openverse/translation-strings": ["error"],
  },
} satisfies TSESLint.Linter.Config
