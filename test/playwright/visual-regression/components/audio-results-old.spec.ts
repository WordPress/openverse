import { test } from '@playwright/test'

import breakpoints from '~~/test/playwright/utils/breakpoints'
import { closeFilters, OLD_HEADER } from '~~/test/playwright/utils/navigation'

test.describe.configure({ mode: 'parallel' })

test.describe('audio results', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/search/audio?q=birds')
  })

  breakpoints.describeEachMobileWithoutMd(
    { uaMocking: false },
    ({ expectSnapshot }) => {
      test('should render small row layout desktop UA with narrow viewport', async ({
        page,
      }) => {
        await expectSnapshot('audio-results-narrow-viewport-desktop-UA', page)
      })
    }
  )

  breakpoints.describeEachMobileWithoutMd(
    { uaMocking: true },
    ({ expectSnapshot }) => {
      test('should render small row layout mobile UA with narrow viewport', async ({
        page,
      }) => {
        await expectSnapshot('audio-results-narrow-viewport-mobile-UA', page)
      })
    }
  )

  breakpoints.describeEachDesktopWithMd(({ expectSnapshot }) => {
    test('desktop audio results', async ({ page }) => {
      await closeFilters(page, OLD_HEADER)
      await expectSnapshot('audio-results-desktop', page)
    })
  })
})
