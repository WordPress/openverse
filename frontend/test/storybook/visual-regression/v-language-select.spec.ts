import { expect } from "@playwright/test"
import { test } from "~~/test/playwright/utils/test"
import { makeGotoWithArgs } from "~~/test/storybook/utils/args"
import { expectSnapshot } from "~~/test/playwright/utils/expect-snapshot"

test.describe("VLanguageSelect", () => {
  test("default", async ({ page }) => {
    await makeGotoWithArgs("components-vlanguageselect--default")(page)
    // Make sure the component is rendered and hydrated
    await expect(page.getByRole("combobox").nth(0)).toBeEnabled()
    await expectSnapshot(
      page,
      "vlanguageselect",
      page.locator(".screenshot-area")
    )
  })
})
