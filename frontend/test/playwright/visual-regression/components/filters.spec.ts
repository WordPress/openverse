import { expect, Page, test } from "@playwright/test"

import {
  goToSearchTerm,
  languageDirections,
} from "~~/test/playwright/utils/navigation"
import breakpoints from "~~/test/playwright/utils/breakpoints"

test.describe.configure({ mode: "parallel" })

const openFiltersTab = async (page: Page) => {
  await page.locator("#content-settings-button").click()
  await page.getByRole("tab").last().click()
}

for (const dir of languageDirections) {
  breakpoints.describeEachDesktop(() => {
    test(`Filters sidebar none selected - ${dir}`, async ({ page }) => {
      await goToSearchTerm(page, "birds", { dir })

      expect(await page.locator(".sidebar").screenshot()).toMatchSnapshot(
        `filters-sidebar-${dir}.png`
      )
    })

    test(`Filters sidebar 1 filter selected - ${dir}`, async ({ page }) => {
      await goToSearchTerm(page, "birds", { dir })
      await page.locator('input[type="checkbox"]').first().check()

      expect(await page.locator(".sidebar").screenshot()).toMatchSnapshot(
        `filters-sidebar-checked-${dir}.png`
      )
    })
  })

  breakpoints.describeEachMobile(({ expectSnapshot }) => {
    test(`Filters modal none selected - ${dir}`, async ({ page }) => {
      await goToSearchTerm(page, "birds", { dir })
      await openFiltersTab(page)

      await expectSnapshot(`filters-modal-${dir}.png`, page)
    })

    test(`Filters modal 1 filter selected - ${dir}`, async ({ page }) => {
      await goToSearchTerm(page, "birds", { dir })
      await openFiltersTab(page)

      await page.locator('input[type="checkbox"]').first().check()

      await expectSnapshot(`filters-modal-filters-selected-${dir}.png`, page)
    })
  })
}
