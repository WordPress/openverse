import { expect, test } from "@playwright/test"

import {
  enableNewHeader,
  goToSearchTerm,
  languageDirections,
  t,
} from "~~/test/playwright/utils/navigation"
import breakpoints from "~~/test/playwright/utils/breakpoints"

test.describe.configure({ mode: "parallel" })

for (const dir of languageDirections) {
  breakpoints.describeEachDesktop(() => {
    test(`Filters sidebar none selected - ${dir}`, async ({ page }) => {
      await enableNewHeader(page)

      await goToSearchTerm(page, "birds", { dir })

      expect(await page.locator(".sidebar").screenshot()).toMatchSnapshot(
        `filters-sidebar-${dir}.png`
      )
    })

    test(`Filters sidebar some filters selected - ${dir}`, async ({ page }) => {
      await enableNewHeader(page)

      await goToSearchTerm(page, "birds", { dir })
      await page.locator('input[type="checkbox"]').first().check()

      expect(await page.locator(".sidebar").screenshot()).toMatchSnapshot(
        `filters-sidebar-checked-${dir}.png`
      )
    })
  })

  breakpoints.describeEachMobile(({ expectSnapshot }) => {
    test(`Filters modal none selected - ${dir}`, async ({ page }) => {
      await enableNewHeader(page)

      await goToSearchTerm(page, "birds", { dir })
      await page.getByRole("button", { name: "Menu" }).click()
      await page.getByRole("tab", { name: t("filters.title", dir) }).click()

      await expectSnapshot(`filters-modal-${dir}.png`, page)
    })

    test(`Filters modal some filters selected - ${dir}`, async ({ page }) => {
      await enableNewHeader(page)

      await goToSearchTerm(page, "birds", { dir })
      await page.getByRole("button", { name: "Menu" }).click()
      await page.getByRole("tab", { name: t("filters.title", dir) }).click()

      await page.locator('input[type="checkbox"]').first().check()

      await expectSnapshot(`filters-modal-filters-selected-${dir}.png`, page)
    })
  })
}
