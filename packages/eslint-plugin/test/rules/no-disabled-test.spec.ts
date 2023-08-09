import { ESLintUtils } from "@typescript-eslint/utils"

import openverseEslintPlugin from "@openverse/eslint-plugin"

const tester = new ESLintUtils.RuleTester({
  parser: "@typescript-eslint/parser",
  rules: {
    "@openverse/no-disabled-test": ["error"],
  },
})

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
        // A skipped test can be precded by multi-line comments:
        // https://github.com/WordPress/openverse/issues/2573
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
]

// Run the tests
tester.run(
  "@openverse/no-disabled-test",
  openverseEslintPlugin.rules["no-disabled-test"],
  {
    valid: validTestCases,
    invalid: invalidTestCases,
  }
)
