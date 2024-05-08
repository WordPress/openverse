/* eslint playwright/expect-expect: ["warn", { "additionalAssertFunctionNames": ["expectSnapshot"] }] */

import { Page, test, expect } from "@playwright/test"

import { makeGotoWithArgs } from "~~/test/storybook/utils/args"

const expectSnapshot = async (name: string, page: Page) => {
  expect(await page.screenshot()).toMatchSnapshot({ name: `${name}.png` })
}

test.describe("VSelectField", () => {
  test("default", async ({ page }) => {
    await makeGotoWithArgs("components-vselectfield--default")(page)
    await expectSnapshot("vselectfield-default", page)
  })

  test("with icon", async ({ page }) => {
    await makeGotoWithArgs("components-vselectfield--with-icon")(page)
    await expectSnapshot("vselectfield-with-icon", page)
  })

  test("without border", async ({ page }) => {
    await makeGotoWithArgs("components-vselectfield--without-border")(page)
    await expectSnapshot("vselectfield-without-border", page)
  })
})
