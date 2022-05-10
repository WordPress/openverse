import { test } from '@playwright/test'

import breakpoints from '~~/test/playwright/utils/breakpoints'
import { removeHiddenOverflow } from '~~/test/playwright/utils/page'
import { dismissTranslationBanner } from '~~/test/playwright/utils/navigation'

const contentPages = ['extension', 'about', 'meta-search', 'search-help']
for (const contentPage of contentPages) {
  test.describe(`${contentPage} page snapshots`, () => {
    test.describe('ltr', () => {
      test.beforeEach(async ({ page }) => {
        await page.goto(`/${contentPage}`)
      })

      breakpoints.describeEvery(({ expectSnapshot }) => {
        test('full page', async ({ page }) => {
          await removeHiddenOverflow(page)
          await expectSnapshot(`${contentPage}-ltr`, page, { fullPage: true })
        })
      })
    })

    test.describe('rtl', () => {
      test.beforeEach(async ({ page }) => {
        await page.goto(`/ar/${contentPage}`)
        await dismissTranslationBanner(page)
      })

      breakpoints.describeEvery(({ expectSnapshot }) => {
        test('full page', async ({ page }) => {
          await removeHiddenOverflow(page)
          await expectSnapshot(`${contentPage}-rtl`, page, { fullPage: true })
        })
      })
    })
  })
}
