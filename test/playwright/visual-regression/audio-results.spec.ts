import { test } from '@playwright/test'

import breakpoints from '~~/test/playwright/utils/breakpoints'

test.describe('audio results', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/search/audio?q=birds')
  })

  breakpoints.describeEachMobile({ uaMocking: false }, ({ expectSnapshot }) => {
    test('should render small row layout desktop UA with narrow viewport', async ({
      page,
    }) => {
      await expectSnapshot('audio-results-narrow-viewport-desktop-UA', page)
    })
  })

  breakpoints.describeEachMobile({ uaMocking: true }, ({ expectSnapshot }) => {
    test('should render small row layout mobile UA with narrow viewport', async ({
      page,
    }) => {
      await expectSnapshot('audio-results-narrow-viewport-mobile-UA', page)
    })
  })

  breakpoints.describeEachDesktop(({ expectSnapshot }) => {
    test('desktop audio results', async ({ page }) => {
      await expectSnapshot('audio-results-desktop', page)
    })
  })
})
