import { RuleTester } from "@typescript-eslint/rule-tester"

import jsoncParser from "jsonc-eslint-parser"

import { translationStrings } from "../../src/rules/translation-strings"

const maxLength = 20

const baseTestCase = {
  filename: "en.json5",
  languageOptions: { parser: jsoncParser },
  options: [
    {
      maxLength,
    },
  ] as const,
}

const tester = new RuleTester()
tester.run("translation-strings", translationStrings, {
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
      languageOptions: { parser: jsoncParser },
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
})
