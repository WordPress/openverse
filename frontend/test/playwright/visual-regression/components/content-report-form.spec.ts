import { Page, test } from "@playwright/test"

import { preparePageForTests } from "~~/test/playwright/utils/navigation"
import breakpoints from "~~/test/playwright/utils/breakpoints"
import { t } from "~~/test/playwright/utils/i18n"

const imageUrl = "/image/feb91b13-422d-46fa-8ef4-cbf1e6ddee9b"

const getReportButton = (page: Page) => {
  return page.getByRole("button", {
    name: t("mediaDetails.contentReport.long"),
  })
}

/**
 * This test was previously known to be flaky:
 * https://github.com/WordPress/openverse/issues/2020
 *
 * The flake involved an offset of 1-2 pixels in both
 * the content and width of the popover (the locator
 * produced with `getReportButton`). To fix this, the
 * test now uses a screenshot of the entire page, rather
 * than the isolated report element, and an increased
 * maxDiffPixel ratio.
 *
 * Additionally, previously there were focused/unfocused
 * tests to confirm the proper focus state of the
 * report popover close button. However, that state
 * only appears on focus visible and the snapshots
 * were identical, so the tests were redundant.
 */
test.describe("content report form", () => {
  test.describe.configure({ retries: 2 })

  breakpoints.describeMd(({ expectSnapshot }) => {
    test("unfocused close button", async ({ page }) => {
      await page.route("**flickr**", (r) => r.abort())

      await preparePageForTests(page, "md")
      await page.goto(imageUrl)

      const button = getReportButton(page)

      // Scroll the button to the bottom of the page
      await button.evaluate((element) => element.scrollIntoView(false))

      await button.click()

      await expectSnapshot("content-report", page, undefined, {
        maxDiffPixelRatio: 0.1,
      })
    })
  })
})
