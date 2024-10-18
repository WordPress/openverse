import * as tseslint from "typescript-eslint"

import unicornPlugin from "eslint-plugin-unicorn"
import playwrightPlugin from "eslint-plugin-playwright"
// @ts-expect-error Vitest is an ECMAScript module, and this file will produce `require` calls
import vitestPlugin from "@vitest/eslint-plugin"
import jsoncPlugin from "eslint-plugin-jsonc"
import eslintCommentsConfigs from "@eslint-community/eslint-plugin-eslint-comments/configs"

import prettierConfig from "eslint-config-prettier"

import globals from "globals"

import typescriptConfig from "./configs/typescript"
import importConfig from "./configs/import"

import vueConfig from "./configs/vue"
import rules from "./rules"

const plugin = {
  configs: {},
  meta: { name: "@openverse", version: "0.0.0" },
  rules: {
    "analytics-configuration": rules["analytics-configuration"],
    "no-unexplained-disabled-test": rules["no-unexplained-disabled-test"],
    "translation-strings": rules["translation-strings"],
  },
}

Object.assign(plugin.configs, {
  project: tseslint.config(
    {
      name: "@openverse/eslint-plugin",
      plugins: {
        "@openverse": plugin,
      },
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
    },
    {
      name: "openverse:common-config",
      plugins: {
        unicorn: unicornPlugin,
        playwright: playwrightPlugin,
      },
      extends: [
        eslintCommentsConfigs.recommended,
        ...typescriptConfig,
        ...importConfig,
        ...jsoncPlugin.configs["flat/recommended-with-jsonc"],
        vitestPlugin.configs.recommended,
      ],
      languageOptions: {
        ecmaVersion: 2022,
        globals: {
          ...globals.node,
          ...globals.browser,
        },
      },
      rules: {
        "no-console": "off",
        "unicorn/filename-case": ["error", { case: "kebabCase" }],
        "unicorn/switch-case-braces": ["error"],
        curly: ["error", "all"],
      },
    },

    {
      name: "openverse:vue-config",
      extends: [...vueConfig],
    },
    prettierConfig,

    {
      name: "openverse:test:packages-unit-tests",
      settings: {
        vitest: {
          typecheck: true,
        },
      },
      languageOptions: {
        globals: {
          ...vitestPlugin.environments.env.globals,
        },
      },
      files: ["packages/js/**/*/test"],
      rules: {
        // Superseded by `@openverse/no-unexplained-disabled-test`
        "vitest/no-disabled-test": "off",
      },
    },
    {
      name: "openverse:test:frontend-unit-tests",
      languageOptions: {
        globals: {
          ...globals.browser,
          ...vitestPlugin.environments.env.globals,
        },
      },
      files: ["frontend/test/unit/**"],
      rules: {
        "import/no-named-as-default-member": ["off"],
        "@intlify/vue-i18n/no-raw-text": ["off"],
        // Superseded by `@openverse/no-unexplained-disabled-test`
        "vitest/no-disabled-test": "off",
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
      name: "openverse:test:playwright",
      files: ["frontend/test/{playwright,storybook}/**"],
      rules: {
        ...playwrightPlugin.configs["flat/recommended"].rules,
        // Superseded by `@openverse/no-unexplained-disabled-test`
        "playwright/no-skipped-test": "off",

        // The following duplicate TypeScript functionality. All our Playwright tests are in TypeScript and type checks will already catch non-string titles.
        "playwright/valid-title": "off",
        "playwright/valid-describe-callback": "off",

        "playwright/expect-expect": [
          "error",
          {
            assertFunctionNames: [
              // Shared assertion for confirming sent events
              "expectEventPayloadToMatch",
              // Shared assertion for visual regression tests
              "expectSnapshot",
              "expectScreenshotAreaSnapshot",
              // Shared assertion for checkbox state
              "expectCheckboxState",
            ],
          },
        ],
      },
    },
    {
      name: "openverse:case:filenames",
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
      name: "openverse:case:components-filenames",
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
    }
  ),
})

export default plugin
