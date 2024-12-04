import { RuleTester } from "@typescript-eslint/rule-tester"
import jsoncParser from "jsonc-eslint-parser"

import { keyNameCasing } from "../../src/rules/key-name-casing"

const tester = new RuleTester()

const baseTestCase = {
  filename: "en.json5",
  languageOptions: { parser: jsoncParser },
}

const invalidCamelCaseKeys = [
  "PascalCase",
  "kebab-case",
  "snake_case",
  "space case",
  "mixed.PascalCase",
  "mixed.kebab-case",
  "mixed.snake_case",
  "mixed.space case",
]

const invalidSnakeCaseKeys = [
  "camelCase",
  "PascalCase",
  "kebab-case",
  "space case",
  "mixed.camelCase",
  "mixed.PascalCase",
  "mixed.kebab-case",
  "mixed.space case",
]

const validCamelCaseKeys = [
  "camelCase",
  "simple",
  "nested.camelCase",
  "deeply.nested.camelCase",
]

const validSnakeCaseKeys = [
  "snake_case",
  "simple",
  "nested.snake_case",
  "deeply.nested.snake_case",
]

tester.run("key-name-casing", keyNameCasing, {
  invalid: [
    // Test camelCase violations
    ...invalidCamelCaseKeys.map(
      (key) =>
        ({
          ...baseTestCase,
          name: `Disallow non-camelCase keys: ${key}`,
          code: `{
            "${key}": "value"
          }`,
          options: [{ camelCaseWithDot: true, snake_case_with_dot: false }],
          errors: [
            {
              messageId: "incorrectKeyNameComment",
              data: {
                name: key,
                formats: "camelCaseWithDot",
              },
            },
          ],
        }) as const
    ),
    // Test snake_case violations
    ...invalidSnakeCaseKeys.map(
      (key) =>
        ({
          ...baseTestCase,
          name: `Disallow non-snake_case keys: ${key}`,
          code: `{
            "${key}": "value"
          }`,
          options: [{ camelCaseWithDot: false, snake_case_with_dot: true }],
          errors: [
            {
              messageId: "incorrectKeyNameComment",
              data: {
                name: key,
                formats: "snake_case_with_dot",
              },
            },
          ],
        }) as const
    ),
  ],
  valid: [
    // Test valid camelCase
    ...validCamelCaseKeys.map(
      (key) =>
        ({
          ...baseTestCase,
          name: `Allow camelCase keys: ${key}`,
          code: `{
            "${key}": "value"
          }`,
          options: [{ camelCaseWithDot: true, snake_case_with_dot: false }],
        }) as const
    ),
    // Test valid snake_case
    ...validSnakeCaseKeys.map(
      (key) =>
        ({
          ...baseTestCase,
          name: `Allow snake_case keys: ${key}`,
          code: `{
            "${key}": "value"
          }`,
          options: [{ camelCaseWithDot: false, snake_case_with_dot: true }],
        }) as const
    ),
    // Test ignored patterns
    {
      ...baseTestCase,
      name: "Allow ignored patterns anywhere in the key",
      code: `{
        "IGNORED_PATTERN": "value",
        "another.IGNORED_PATTERN": "value",
        "IGNORED_PATTERN.something": "value"
      }`,
      options: [
        {
          camelCaseWithDot: true,
          snake_case_with_dot: true,
          ignores: ["IGNORED_PATTERN"],
        },
      ],
    },
  ],
})
