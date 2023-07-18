const { RuleTester } = require("eslint")

const rule = require("../../src/rules/no-disabled-test")

const ruleTester = new RuleTester({
  parserOptions: { ecmaVersion: 2018 },
})

ruleTester.run("no-disabled-test", rule, {
  valid: [
    'test("valid test", () => { /* implementation */ });',
    `
    // https://github.com/WordPress/openverse/issues/2573
    test.skip('valid skipped test', () => {
        /* implementation */
    });
    `,
    `
    describe('my beverage', () => {
      test('is delicious', () => {
        expect(myBeverage.delicious).toBeTruthy();
      });
    
      test('is not sour', () => {
        expect(myBeverage.sour).toBeFalsy();
      });
    });
    `,
    `
    // https://github.com/WordPress/openverse/issues/2573
    describe.skip('my other beverage', () => {
      // ... will be skipped
    });
    `,
    `
    // https://github.com/WordPress/openverse/issues/2573
    test.skip.each([
      [1, 1, 2],
      [1, 2, 3],
      [2, 1, 3],
    ])('.add(%i, %i)', (a, b, expected) => {
      expect(a + b).toBe(expected); // will not be run
    });
    `,
    `
    test('will be run', () => {
      expect(1 / 0).toBe(Infinity);
    });
    `,
    `
    // A skipped test can be precded by multi-line comments:
    // https://github.com/WordPress/openverse/issues/2573
    describe.skip.each([
      [1, 1, 2],
      [1, 2, 3],
      [2, 1, 3],
    ])('.add(%i, %i)', (a, b, expected) => {
      test(\`returns \${expected}\`, () => {
        expect(a + b).toBe(expected); // will not be run
      });
    });
    `,
    `
    // https://github.com/WordPress/openverse/issues/2573
    test.concurrent.skip.each([
      [1, 1, 2],
      [1, 2, 3],
      [2, 1, 3],
    ])('.add(%i, %i)', async (a, b, expected) => {
      expect(a + b).toBe(expected); // will not be run
    });
    `,
    `
    // Please note this test is skipped because of this issue: https://github.com/WordPress/openverse/issues/2573
    test.skip('it is not snowing', () => {
      expect(inchesOfSnow()).toBe(0);
    });
    `,
  ],
  invalid: [
    {
      code: `
      test.skip('invalid skipped test', () => {
        // Some comments without issue link
      });
      `,
      errors: [
        {
          message:
            "Disabled tests must have an issue comment with a GitHub link preceding them.",
        },
      ],
    },
    {
      code: `
      test.todo('invalid todo test', () => {
        // Some comments
      });
      `,
      errors: [
        {
          message:
            "Disabled tests must have an issue comment with a GitHub link preceding them.",
        },
      ],
    },
    {
      code: `
      test.skip.each([
        [1, 1, 2],
        [1, 2, 3],
        [2, 1, 3],
      ])('.add(%i, %i)', (a, b, expected) => {
        expect(a + b).toBe(expected); // will not be run
      });
      `,
      errors: [
        {
          message:
            "Disabled tests must have an issue comment with a GitHub link preceding them.",
        },
      ],
    },
    {
      code: `
      test.skip("invalid skipped test 1", async () => {
        // ...
      });
      test("valid test", () => {
        // ...
      });
      test.skip("invalid skipped test 2", async () => {
        // ...
      });
      `,
      errors: [
        {
          message:
            "Disabled tests must have an issue comment with a GitHub link preceding them.",
        },
        {
          message:
            "Disabled tests must have an issue comment with a GitHub link preceding them.",
        },
      ],
    },
  ],
})
