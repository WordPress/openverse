import tseslint, { plugin, configs as tsConfigs } from "typescript-eslint"
import tsdocPlugin from "eslint-plugin-tsdoc"
import eslint from "@eslint/js"

export default tseslint.config(
  {
    plugins: {
      "@typescript-eslint": plugin,
      tsdoc: tsdocPlugin,
    },
  },
  {
    name: "vue-typescript",
    files: ["**/*.ts", "**/*.js", "**/*.mjs", "**/*.vue"],
    extends: [eslint.configs.recommended, ...tsConfigs.recommended],
    rules: {
      "@typescript-eslint/no-require-imports": ["off"],
    },
  },
  {
    name: "tsdoc-syntax-no-require-imports",
    files: ["**/*.ts"],
    extends: [...tsConfigs.recommended],
    rules: {
      "tsdoc/syntax": "error",
      // This rule is disabled above to avoid forcing ESM syntax on regular JS files
      // that aren't ready for it yet. We do want to enforce this for TypeScript,
      // however, so we re-enable it here.
      "@typescript-eslint/no-require-imports": ["error"],
    },
  }
)
