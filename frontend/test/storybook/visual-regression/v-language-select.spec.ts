import { Page, test, expect } from "@playwright/test"

import { makeGotoWithArgs } from "~~/test/storybook/utils/args"

const expectSnapshot = async (name: string, page: Page) => {
  expect(await page.screenshot()).toMatchSnapshot({ name: `${name}.png` })
}

test.describe("VLanguageSelect", () => {
  test("default", async ({ page }) => {
    await makeGotoWithArgs("components-vlanguageselect--default")(page)
    await expectSnapshot("vlanguageselect-default", page)
  })
})
