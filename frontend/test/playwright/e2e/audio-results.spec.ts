import { expect, test } from "@playwright/test"

import {
  goToSearchTerm,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"
import {
  locateFocusedResult,
  walkToType,
} from "~~/test/playwright/utils/search-results"

test.describe.configure({ mode: "parallel" })

test.describe("all results grid keyboard accessibility test", () => {
  test.beforeEach(async ({ page }) => {
    await preparePageForTests(page, "xl")
    await goToSearchTerm(page, "birds")
  })

  test("should show instructions snackbar when focusing first audio", async ({
    page,
  }) => {
    await walkToType("audio", page)

    await expect(page.locator("[role=alert]")).toBeVisible()
  })

  test("should hide the instructions snackbar when interacted with audio", async ({
    page,
  }) => {
    await walkToType("audio", page)

    await expect(page.locator("[role=alert]")).toBeVisible()

    const focusedResult = await locateFocusedResult(page)

    await focusedResult.press("Space")

    await expect(page.locator("[role=alert]")).toBeHidden()
  })
})
