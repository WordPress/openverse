import { Page, test, expect } from "@playwright/test"

import { makeGotoWithArgs } from "~~/test/storybook/utils/args"

const expectSnapshot = async (name: string, page: Page) => {
  expect(await page.screenshot()).toMatchSnapshot({
    name: `${name}.png`,
    maxDiffPixelRatio: 0.01, // for flake and variability in the component width
  })
}

test.describe("VLanguageSelect", () => {
  test("default", async ({ page }) => {
    await makeGotoWithArgs("components-vlanguageselect--default-story")(page)
    await expectSnapshot("vlanguageselect-default", page)
  })
})
