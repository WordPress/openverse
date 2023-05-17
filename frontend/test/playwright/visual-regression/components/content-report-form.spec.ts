import { Page, test } from "@playwright/test"

import { t } from "~~/test/playwright/utils/navigation"
import breakpoints from "~~/test/playwright/utils/breakpoints"

const imageUrl = "/image/feb91b13-422d-46fa-8ef4-cbf1e6ddee9b"

const getReportButton = (page: Page) => {
  return page.getByRole("button", {
    name: t("media-details.content-report.long"),
  })
}

const getReportForm = (page: Page) => {
  return page.getByRole("dialog", {
    name: t("media-details.content-report.long"),
  })
}

breakpoints.describeMd(({ expectSnapshot }) => {
  test("unfocused close button", async ({ page }) => {
    await page.goto(imageUrl)

    await getReportButton(page).click()

    await expectSnapshot("content-report-unfocused", getReportForm(page))
  })
})

test.describe("content report form", () => {
  // Flaky: https://github.com/WordPress/openverse/issues/2020
  test.describe.configure({ retries: 2 })

  breakpoints.describeMd(({ expectSnapshot }) => {
    test("focused close button", async ({ page }) => {
      await page.goto(imageUrl)

      await getReportButton(page).click()

      const form = getReportForm(page)

      await form.getByRole("button", { name: t("modal.close") }).focus()

      await expectSnapshot("content-report-focused", form)
    })
  })
})
