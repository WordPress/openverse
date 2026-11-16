import { expect } from "@playwright/test"
import { test } from "~~/test/playwright/utils/test"
import breakpoints from "~~/test/playwright/utils/breakpoints"
import {
  goToSearchTerm,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"
import { skipToContentLink } from "~~/test/playwright/utils/components"

import { skipToContentTargetId } from "#shared/constants/window"
import { keycodes } from "#shared/constants/key-codes"

test.describe.configure({ mode: "parallel" })

/** Test one of each:
 * - search page (all media and single media type)
 * - single result page
 * - content page
 * - home page
 * - collection page (image)
 */
const pages = [
  ["/search/image?q=galah", "MAIN"],
  ["/search/audio?q=galah", "MAIN"],
  ["/search/?q=galah", "MAIN"],
  ["/", "DIV"],
  ["/image/e9d97a98-621b-4ec2-bf70-f47a74380452", "MAIN"],
  ["/about", "MAIN"],
  ["/image/collection?collection=tag&tag=cat", "MAIN"],
] as const

for (const [pageUrl, contentTag] of pages) {
  breakpoints.describeMobileAndDesktop(async ({ breakpoint }) => {
    test(`can skip to content on ${pageUrl}`, async ({ page }) => {
      await preparePageForTests(page, breakpoint, {
        features: { fetch_sensitive: "off" },
      })

      await page.goto(pageUrl)

      const main = page.getByRole("main")
      const content = page.locator(`#${skipToContentTargetId}`)
      await expect(main).toHaveCount(1)
      await expect(content).toHaveJSProperty("tagName", contentTag)
      await expect(content).toHaveAttribute("tabindex", "-1")
      await expect(
        page.locator(
          `main#${skipToContentTargetId}, main #${skipToContentTargetId}`
        )
      ).toHaveCount(1)

      // Tab to the skip to content button
      await page.keyboard.press(keycodes.Tab)

      await expect(skipToContentLink(page)).toBeFocused()

      // We cannot check if the screen reader cursor has moved to the content
      // because Playwright does not support this, and when you click on
      // skip-to-content button, body becomes the active element.
      // This is why we simply check that there's a visible element with
      // id="content" on the page.
      await expect(content).toBeVisible()
    })
  })
}

test("search main landmark is the skip target after client-side navigation", async ({
  page,
}) => {
  await preparePageForTests(page, "xl")
  await goToSearchTerm(page, "galah", { mode: "CSR" })

  const main = page.getByRole("main")
  await expect(main).toHaveCount(1)
  await expect(main).toHaveAttribute("id", skipToContentTargetId)
  await expect(main).toHaveAttribute("tabindex", "-1")
  await expect(main.getByTestId("search-results")).toBeVisible()
  await expect(skipToContentLink(page)).toHaveAttribute(
    "href",
    `#${skipToContentTargetId}`
  )
})
