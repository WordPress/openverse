import { expect } from "@playwright/test"
import { test } from "~~/test/playwright/utils/test"
import { expectSnapshot } from "~~/test/playwright/utils/expect-snapshot"

test.describe("VIconButton", () => {
  const url = "/iframe.html?id=components-viconbutton--sizes"

  test("icon button sizes", async ({ page }) => {
    await page.goto(url)

    // Wait for buttons to be hydrated
    await expect(page.getByRole("button")).toHaveCount(3)
    await expect(page.getByRole("button").nth(0)).toBeEnabled()
    await expectSnapshot(
      page,
      "v-icon-button-sizes",
      page.locator(".screenshot-area")
    )
  })
})
