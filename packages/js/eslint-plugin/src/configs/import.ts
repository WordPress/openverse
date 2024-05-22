import type { TSESLint } from "@typescript-eslint/utils"

/**
 * ESLint `import` plugin configuration.
 */
export = {
  extends: ["plugin:import/recommended", "plugin:import/typescript"],
  plugins: ["import"],
  rules: {
    // `namespace` and `default` are handled by TypeScript
    // There's no need to rely on ESLint for this
    // https://github.com/import-js/eslint-plugin-import/issues/2878
    "import/namespace": "off",
    "import/default": "off",
    "import/newline-after-import": ["error"],
    "import/order": [
      "error",
      {
        "newlines-between": "always-and-inside-groups",
        groups: [
          "builtin",
          "external",
          "internal",
          "parent",
          "sibling",
          "index",
          "object",
          "type",
        ],
        pathGroups: [
          {
            // Treat vue and composition-api as "builtin"
            pattern: "(vue|@nuxtjs/composition-api)",
            group: "builtin",
            position: "before",
          },
          {
            // Move assets to the very end of the imports list
            pattern: "~/assets/**",
            group: "type",
            position: "after",
          },
          {
            // Treat components as their own group and move to the end of the internal imports list
            pattern: "~/components/**",
            group: "internal",
            position: "after",
          },
          /**
           * These next two must come after any more specific matchers
           * as the plugin uses the patterns in order and does not sort
           * multiple-matches by specificity, it just takes the _first_
           * pattern that matches and applies that group to the import.
           */
          {
            // Document webpack alias
            pattern: "~/**",
            group: "internal",
            position: "before",
          },
          {
            // Document webpack alias
            pattern: "~~/**",
            group: "external",
            position: "after",
          },
        ],
      },
    ],
    "import/extensions": ["error", "always", { js: "never", ts: "never" }],
  },
  overrides: [
    {
      files: ["frontend/**"],
      settings: {
        "import/resolver": {
          typescript: {
            project: "frontend/tsconfig.json",
            extensions: [".js", ".ts", ".vue", ".png"],
          },
        },
      },
    },
    {
      files: ["packages/js/**"],
      settings: {
        "import/resolver": {
          typescript: {
            project: "packages/js/*/tsconfig.json",
          },
        },
      },
    },
    {
      files: ["frontend/.storybook/**"],
      rules: {
        /**
         * `.nuxt-storybook` doesn't exist in the CI when it
         * lints files unless we ran the storybook build before linting,
         * meaning that the imports used in the modules in this directory
         * are mostly unavailable.
         *
         * To avoid turning these rules off we'd have to run the storybook
         * build in CI before linting (or even instruct people to run
         * storybook build locally before trying to lint) and that's just too
         * heavy a lift when we can instead disable the rules for just this
         * directory.
         *
         * Note: This means that if you disable these changes and have not
         * deleted the `.nuxt-storybook` directory locally, you will not see
         * any ESLint errors. That does not mean these rules are unnecessary.
         * Delete the `frontend/.nuxt-storybook` directory and re-run ESLint
         * with these rule changes commented out: now you will see the errors
         * present in CI.
         */
        "import/extensions": "off",
        "import/export": "off",
        "import/no-unresolved": "off",
      },
    },
  ],
} satisfies TSESLint.Linter.Config
