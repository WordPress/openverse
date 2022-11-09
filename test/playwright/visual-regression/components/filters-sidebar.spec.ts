import { test, expect } from '@playwright/test'

import {
  goToSearchTerm,
  languageDirections,
} from '~~/test/playwright/utils/navigation'

test.describe.configure({ mode: 'parallel' })

for (const dir of languageDirections) {
  test(`Filters sidebar none selected - ${dir}`, async ({ page }) => {
    await goToSearchTerm(page, 'birds', { dir })

    expect(await page.locator('.sidebar').screenshot()).toMatchSnapshot({
      name: `filters-sidebar-${dir}.png`,
    })
  })
  test(`Filters sidebar some filters selected - ${dir}`, async ({ page }) => {
    await goToSearchTerm(page, 'birds', { dir })
    await page.locator('input[type="checkbox"]').first().check()

    expect(await page.locator('.sidebar').screenshot()).toMatchSnapshot({
      name: `filters-sidebar-filters-selected-${dir}.png`,
    })
  })
}
