import { test, expect } from "@playwright/test"

import { makeGotoWithArgs } from "~~/test/storybook/utils/args"
import { expectSnapshot } from "~~/test/storybook/utils/expect-snapshot"

for (const slug of ["default", "with-icon", "without-border"]) {
  test(`vselectfield-${slug}`, async ({ page }) => {
    await makeGotoWithArgs(`components-vselectfield--${slug}`)(page)
    await expect(page.getByRole("combobox").nth(0)).toBeEnabled()
    await expectSnapshot(
      `vselectfield-${slug}`,
      page.locator(".screenshot-area")
    )
  })
}
