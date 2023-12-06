import type { TSESLint } from "@typescript-eslint/utils"

/**
 * The Openverse project's ESLint configuration.
 *
 * This configuration is split into sub-modules in this directory
 * that are included using `require.resolve`.
 */
export const project: TSESLint.Linter.Config = {
  env: {
    browser: true,
    node: true,
  },
  parser: "vue-eslint-parser",
  extends: [
    "eslint:recommended",
    "plugin:eslint-comments/recommended",
    "plugin:jsonc/recommended-with-jsonc",
    require.resolve("./custom"),
    require.resolve("./vue"),
    require.resolve("./import"),
    require.resolve("./typescript"),
    "prettier",
  ],
  plugins: ["unicorn"],
  settings: {
    "vue-i18n": {
      localeDir: "./frontend/src/locales/*.{json}",
      messageSyntaxVersion: "^8.24.3",
    },
  },
  rules: {
    semi: ["error", "never"],
    "no-console": "off",
    "unicorn/filename-case": ["error", { case: "kebabCase" }],
    "unicorn/switch-case-braces": ["error"],
    "curly": ["error", "all"]
  },
  overrides: [
    {
      files: ["*.json", "*.json5", "*.jsonc"],
      parser: "jsonc-eslint-parser",
    },
    {
      env: { jest: true },
      files: ["packages/**/*/test", "frontend/test/unit/**"],
      plugins: ["jest"],
      extends: ["plugin:jest/recommended"],
      rules: {
        "import/no-named-as-default-member": ["off"],
        "@intlify/vue-i18n/no-raw-text": ["off"],
        // Superseded by `@openverse/no-unexplained-disabled-test`
        "jest/no-disabled-test": "off",
        "no-restricted-imports": [
          "error",
          {
            name: "pinia",
            message:
              "Please import pinia test utils from `~~/test/unit/test-utils/pinia`. The test-utils version ensures proper setup of universally necessary Nuxt context mocks.",
          },
        ],
        "no-restricted-syntax": [
          "error",
          {
            selector:
              "ImportDeclaration[source.value='@vue/test-utils']:has(ImportSpecifier[local.name='shallowMount'])",
            message:
              "Do not use @vue/test-utils' `shallowMount`. Use `~~/test/unit/test-utils/render` instead which includes helpful context setup or @testing-library/vue's `render` directly.",
          },
        ],
      },
    },
    {
      files: ["frontend/test/{playwright,storybook}/**"],
      plugins: ["playwright"],
      extends: ["plugin:playwright/recommended"],
      rules: {
        // Superseded by `@openverse/no-unexplained-disabled-test`
        "playwright/no-skipped-test": "off",
      },
      settings: {
        playwright: {
          additionalAssertFunctionNames: [
            // Shared assertion for confirming sent events
            "expectEventPayloadToMatch",
            // Shared assertion for visual regression tests
            "expectSnapshot",
          ],
        },
      },
    },
    {
      files: [
        "automations/js/src/**",
        "frontend/test/**",
        "frontend/src/**/**.json",
      ],
      rules: {
        "unicorn/filename-case": "off",
      },
    },
    {
      files: ["frontend/src/components/**"],
      rules: {
        "unicorn/filename-case": [
          "error",
          // Allow things like `Component.stories.js` and `Component.types.js`
          {
            case: "pascalCase",
            ignore: [".eslintrc.js", ".*\\..*\\.js", ".*\\.json"],
          },
        ],
      },
    },
    {
      files: [
        "frontend/src/locales/scripts/en.json5",
        "frontend/test/locales/*.json",
      ],
      rules: {
        "jsonc/key-name-casing": [
          "error",
          {
            camelCase: true,
            "kebab-case": false,
            snake_case: true, // for err_* keys
            ignores: ["ncSampling+", "sampling+"],
          },
        ],
      },
    },
    {
      files: ["frontend/src/locales/scripts/en.json5"],
      rules: {
        "jsonc/quote-props": "off",
        "jsonc/quotes": "off",
      },
    },
  ],
}
