import { expect, test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"

import { preparePageForTests } from "~~/test/playwright/utils/navigation"

import { keycodes } from "~/constants/key-codes"
import { skipToContentTargetId } from "~/constants/window"

test.describe.configure({ mode: "parallel" })

/** Test one of each:
 * - search page (all media and single media type)
 * - single result page
 * - content page
 * - home page
 */
const pages = [
  "/search/image?q=galah",
  "/search?q=galah",
  "/",
  "/image/e9d97a98-621b-4ec2-bf70-f47a74380452",
  "/about",
]

for (const pageUrl of pages) {
  breakpoints.describeMobileAndDesktop(async ({ breakpoint }) => {
    test(`can skip to content on ${pageUrl}`, async ({ page }) => {
      await preparePageForTests(page, breakpoint, {
        features: { fetch_sensitive: "off" },
      })

      await page.goto(pageUrl)

      // Tab to the skip to content button
      await page.keyboard.press(keycodes.Tab)

      await expect(
        page.getByRole("link", { name: "Skip to content" })
      ).toBeFocused()

      // We cannot check if the screen reader cursor has moved to the content
      // because Playwright does not support this, and when you click on
      // skip-to-content button, body becomes the active element.
      // This is why we simply check that there's a visible element with
      // id="content" on the page.
      await expect(page.locator(`#${skipToContentTargetId}`)).toBeVisible()
    })
  })
}
