import { test } from "~~/test/playwright/utils/test-fixture"

import breakpoints from "~~/test/playwright/utils/breakpoints"
import { setBreakpointCookie } from "~~/test/playwright/utils/navigation"

test.describe.configure({ mode: "parallel" })

breakpoints.describeEvery(({ breakpoint, expectSnapshot }) => {
  test.beforeEach(async ({ page }) => {
    await setBreakpointCookie(page, breakpoint)
    await page.goto("/ru/search/?q=birds&referrer=creativecommons.org")
  })

  test("page with all banners", async ({ page }) => {
    await expectSnapshot(`page-with-all-banners`, page)
  })
})
