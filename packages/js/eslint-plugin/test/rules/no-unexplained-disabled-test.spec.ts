import { RuleTester } from "@typescript-eslint/rule-tester"

import { noUnexplainedDisabledTest } from "../../src/rules/no-unexplained-disabled-test"

const tester = new RuleTester()

const invalidTestCases = [
  {
    name: "Test with missing issue comment",
    code: `
      test.skip('invalid test case', () => {
        // Some comments without issue link
      });
    `,
    errors: [{ messageId: "missingIssueComment" } as const],
  },
  {
    name: "Test with missing issue comment on .skip.each test",
    code: `
        test.skip.each([
        [1, 1, 2],
        [1, 2, 3],
        [2, 1, 3],
        ])('.add(%i, %i)', (a, b, expected) => {
        expect(a + b).toBe(expected) // will not be run
        })
    `,
    errors: [{ messageId: "missingIssueComment" } as const],
  },
  {
    name: "Test with missing issue comment on test.todo",
    code: `
        test.todo('invalid todo test', () => {
        // Some comments
        })
    `,
    errors: [{ messageId: "missingIssueComment" } as const],
  },
  {
    name: "Test with missing issue comment on describe.skip",
    code: `
        describe.skip('my other beverage', () => {
        // ... will be skipped
        })
    `,
    errors: [{ messageId: "missingIssueComment" } as const],
  },
  {
    name: "Nested blocks with multiple skipped tests shows multiple errors",
    code: `
      describe("block", () => {
        test("no skipped", () => {})

        test.skip("first skipped", () => {})

        test("also not skipped", () => {})

        test.skip("second skipped", () => {})
      })
    `,
    errors: [
      { messageId: "missingIssueComment" },
      { messageId: "missingIssueComment" },
    ] as const,
  },
  {
    name: "Skipped external block and skipped nested block have separate errors",
    code: `
      test.skip("external skip", () => {})

      describe("block", () => {
        test("not skipped", () => {})

        test.skip("nested skip", () => {})
      })
    `,
    errors: [
      { messageId: "missingIssueComment" },
      { messageId: "missingIssueComment" },
    ] as const,
  },
]

const validTestCases = [
  {
    name: "Test describe.skip with valid issue comment",
    code: `
        // https://github.com/WordPress/openverse/issues/2573
        describe.skip('my other beverage', () => {
        // ... will be skipped
        })
    `,
  },
  {
    name: "Test .skip.each with valid issue comment",
    code: `
        // https://github.com/WordPress/openverse/issues/2573
        test.skip.each([
        [1, 1, 2],
        [1, 2, 3],
        [2, 1, 3],
        ])('.add(%i, %i)', (a, b, expected) => {
        expect(a + b).toBe(expected) // will not be run
        })
    `,
  },
  {
    name: "Test .skip with valid issue comment",
    code: `
      // https://github.com/your-org/your-repo/issues/123
      test.skip('valid test case', () => {
        // Test implementation
      });
    `,
  },
  {
    name: "Test with valid issue comment preceded by comment",
    code: `
        /* A skipped test can be precded by multi-line comments:
           https://github.com/WordPress/openverse/issues/2573
        */
        describe.skip.each([
        [1, 1, 2],
        [1, 2, 3],
        [2, 1, 3],
        ])('.add(%i, %i)', (a, b, expected) => {
        test(\`returns \${expected}\`, () => {
            expect(a + b).toBe(expected) // will not be run
        })
        })
    `,
  },
  {
    name: "Test concurrent.skip with valid issue comment",
    code: `
        // https://github.com/WordPress/openverse/issues/2573
        test.concurrent.skip.each([
        [1, 1, 2],
        [1, 2, 3],
        [2, 1, 3],
        ])('.add(%i, %i)', async (a, b, expected) => {
        expect(a + b).toBe(expected) // will not be run
        })
    `,
  },
  {
    name: "Nested skip valid with comment on skipped test",
    code: `
      describe("group of tests", () => {
        // https://github.com/WordPress/openverse/issues/2573
        test.skip("skipped", () => {})
      })
    `,
  },
  {
    name: "Nested and external blocks do not error",
    code: `
      // https://github.com/WordPress/openverse/issues/2573
      test.skip("external skip", () => {})

      describe("block", () => {
        test("not skipped", () => {})

        // https://github.com/WordPress/openverse/issues/2573
        test.skip("nested skip", () => {})
      })
    `,
  },
]

// Run the tests
tester.run("no-unexplained-disabled-test", noUnexplainedDisabledTest, {
  valid: validTestCases,
  invalid: invalidTestCases,
})
