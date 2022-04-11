import { test } from '@playwright/test'

import breakpoints from '~~/test/playwright/utils/breakpoints'
import { removeHiddenOverflow } from '~~/test/playwright/utils/page'

test.describe('sources page snapshots', () => {
  test.describe('ltr', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/sources')
    })

    breakpoints.describeEvery(({ expectSnapshot }) => {
      test('top', async ({ page }) => {
        await removeHiddenOverflow(page)
        await expectSnapshot('sources-ltr', page, { fullPage: true })
      })
    })
  })

  test.describe('rtl', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/ar/sources')
    })

    breakpoints.describeEvery(({ expectSnapshot }) => {
      test('top', async ({ page }) => {
        await removeHiddenOverflow(page)
        await expectSnapshot('sources-rtl', page, { fullPage: true })
      })
    })
  })
})
