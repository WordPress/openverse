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

const getReportForm = (page: Page) => {
  return page.getByRole("dialog", {
    name: t("mediaDetails.contentReport.long"),
  })
}

/**
 * This test was previoiusly known to be flaky:
 * https://github.com/WordPress/openverse/issues/2020
 *
 * The flake involved an offset of 1-2 pixels in both
 * the content and width of the popover (the locator
 * produced with `getReportButton`). To fix this, the
 * test now uses a screenshot of the entire page, rather
 * than the isolated report element, and an increased
 * maxDiffPixel ratio.
 */
test.describe("content report form", () => {
  test.describe.configure({ retries: 2 })

  breakpoints.describeMd(({ expectSnapshot }) => {
    test("unfocused close button", async ({ page }) => {
      await preparePageForTests(page, "md")
      await page.goto(imageUrl)

      await getReportButton(page).click()

      await expectSnapshot("content-report-unfocused", page, undefined, {
        maxDiffPixelRatio: 0.1,
      })
    })
  })

  breakpoints.describeMd(({ expectSnapshot }) => {
    test("focused close button", async ({ page }) => {
      await preparePageForTests(page, "md")
      await page.goto(imageUrl)

      await getReportButton(page).click()

      const form = getReportForm(page)

      await form.getByRole("button", { name: t("modal.close") }).focus()

      await expectSnapshot("content-report-focused", page, undefined, {
        maxDiffPixelRatio: 0.1,
      })
    })
  })
})
