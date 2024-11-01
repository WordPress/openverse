import { RuleTester } from "@typescript-eslint/rule-tester"

import { analyticsConfiguration } from "../../src/rules/analytics-configuration"

const tester = new RuleTester()

const baseTestCase = {
  filename: "types/analytics.ts",
}

const invalidEventNames = [
  "not_screaming_snake_case",
  "'not snake case'",
  "'NOT SNAKE CASE CAPS'",
  "'kebab-case'",
  "'SCREAMING-KEBAB'",
  "_STARTS_UNDERSCORE",
  "ENDS_UNDERSCORE_",
]

const validEventNames = [
  "SCREAMING_SNAKE_CASE",
  "SINGLEWORD",
  "REPEATED__DELIMITER",
]

const invalidPayloadTypes = ["{}", "null", "undefined"]

const invalidPayloadValueTypes = [
  "{}",
  "'string literal'",
  "10", // number literal,
  "null",
  "undefined",
  "true",
]

const validPayloadValueTypes = ["string", "number", "boolean"]

const mockReservedPropNames = ["timestamp", "ua"]

tester.run("analytics-configuration", analyticsConfiguration, {
  invalid: [
    ...invalidEventNames.map(
      (eventName) =>
        ({
          ...baseTestCase,
          name: `Disallow event names not in screaming snake case: ${eventName}`,
          code: `
        export type Events = {
          ${eventName}: never
        }
      `,
          errors: [
            {
              messageId: "eventNameFormat",
              data: { eventName: eventName.replace(/'/g, "") },
            },
          ],
        }) as const
    ),
    ...invalidPayloadTypes.map(
      (payloadType) =>
        ({
          ...baseTestCase,
          name: `Disallow ${payloadType} as payload types.`,
          code: `
        export type Events = {
          EVENT_NAME: ${payloadType}
        }
      `,
          errors: [{ messageId: "emptyPayloadType" }],
        }) as const
    ),
    ...mockReservedPropNames.map(
      (propName) =>
        ({
          ...baseTestCase,
          options: [
            {
              reservedPropNames: mockReservedPropNames,
            },
          ],
          name: `Disallow reserved prop name ${propName} (configured via rule test options)`,
          code: `
        export type Events = {
          EVENT_NAME: {
            ${propName}: number
          }
        }
      `,
          errors: [
            { messageId: "reservedPayloadPropNames", data: { propName } },
          ],
        }) as const
    ),
    ...invalidPayloadValueTypes.map(
      (payloadPropType) =>
        ({
          ...baseTestCase,
          name: `Disallow ${payloadPropType} payload prop type`,
          code: `
        export type Events = {
          EVENT_NAME: {
            payloadProp: ${payloadPropType}
          }
        }
      `,
          errors: [{ messageId: "invalidPayloadFormat" }],
        }) as const
    ),
  ],
  valid: [
    ...validEventNames.map(
      (eventName) =>
        ({
          ...baseTestCase,
          name: `Allow screaming snake case variations: ${eventName}`,
          code: `
        export type Events = {
          ${eventName}: never
        }
      `,
        }) as const
    ),
    {
      ...baseTestCase,
      name: "Use `never` for empty payloads.",
      code: `
        export type Events = {
          EVENT_NAME: never
        }
      `,
    },
    {
      ...baseTestCase,
      options: [
        {
          reservedPropNames: mockReservedPropNames,
        },
      ],
      name: "Allow other prop names even if some are reserved",
      code: `
        export type Events = {
          EVENT_NAME: {
            not_reserved: string
            another: number
          }
        }
      `,
    },
    ...validPayloadValueTypes.map(
      (payloadPropType) =>
        ({
          ...baseTestCase,
          name: `Allow payload prop type ${payloadPropType}`,
          code: `
        export type Events = {
          EVENT_NAME: {
            prop: ${payloadPropType}
          }
        }
      `,
        }) as const
    ),
  ],
})
