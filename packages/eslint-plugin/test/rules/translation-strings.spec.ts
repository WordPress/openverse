import { RuleTester } from "@typescript-eslint/rule-tester"

import openverseEslintPlugin from "@openverse/eslint-plugin"

const maxLength = 20

const tester = new RuleTester({
  parser: "jsonc-eslint-parser",
  rules: {
    "@openverse/translation-strings": ["error"],
  },
})

const baseTestCase = {
  filename: "en.json5",
  options: [
    {
      maxLength,
    },
  ] as const,
}

tester.run(
  "@openverse/translation-strings",
  openverseEslintPlugin.rules["translation-strings"],
  {
    invalid: [
      {
        ...baseTestCase,
        name: "Disallow strings longer than configured max length",
        code: `
          {
            hello: {
              world: {
                this: {
                  is: {
                    tooLong: "${new Array(maxLength + 1)
                      .fill("word")
                      .join(" ")}"
                  }
                }
              }
            }
          }
        `,
        errors: [{ messageId: "maxLengthExceeded", data: { maxLength } }],
      },
      {
        ...baseTestCase,
        name: "Disallow strings longer than configured max length, less property nesting",
        code: `
        {
          tooLong: "${new Array(maxLength + 1).fill("word").join(" ")}"
        }`,
        errors: [
          {
            messageId: "maxLengthExceeded",
            data: { maxLength },
          },
        ],
      },
    ],
    valid: [
      {
        ...baseTestCase,
        name: "Does not exceed configured max length",
        code: `
          {
            hello: {
              world: {
                this: {
                  isNot: {
                    tooLong: "${new Array(maxLength - 1)
                      .fill("word")
                      .join(" ")}"
                  }
                }
              }
            }
          }
        `,
      },
      {
        filename: "notEnjson5.json5",
        name: "Ignores files that are not en.json5",
        code: `
        {
          hello: {
            world: {
              this: {
                isTooLong: "${new Array(maxLength + 1).fill("word").join(" ")}"
              }
            }
          }
        }`,
      },
    ],
  }
)
