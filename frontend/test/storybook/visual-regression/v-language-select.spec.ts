import { expect, test } from "@playwright/test"

import { makeGotoWithArgs } from "~~/test/storybook/utils/args"
import { expectSnapshot } from "~~/test/storybook/utils/expect-snapshot"

test.describe("VLanguageSelect", () => {
  test("default", async ({ page }) => {
    await makeGotoWithArgs("components-vlanguageselect--default")(page)
    // Make sure the component is rendered and hydrated
    await expect(page.getByRole("combobox").nth(0)).toBeEnabled()
    await expectSnapshot("vlanguageselect", page.locator(".screenshot-area"))
  })
})
