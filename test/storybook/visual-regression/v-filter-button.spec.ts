import { test } from '@playwright/test'

import breakpoints from '~~/test/playwright/utils/breakpoints'
import { makeGotoWithArgs } from '~~/test/storybook/utils/args'

const gotoWithArgs = makeGotoWithArgs(
  'components-vheader-vfilterbutton--default-story'
)

test.describe('VFilterButton', () => {
  breakpoints.describeMd(({ expectSnapshot }) => {
    test('no filters applied', async ({ page }) => {
      await gotoWithArgs(page, { isMinMd: true })
      await expectSnapshot('filter-button-at-rest', page)
    })

    test('no filters pressed', async ({ page }) => {
      await gotoWithArgs(page, { isMinMd: true, pressed: true })
      await expectSnapshot('filter-button-pressed', page)
    })

    test('filters applied', async ({ page }) => {
      await gotoWithArgs(page, { isMinMd: true, appliedFilters: 2 })
      await expectSnapshot('filter-button-2-filters', page)
    })

    test('filters applied and pressed', async ({ page }) => {
      await gotoWithArgs(page, {
        isMinMd: true,
        appliedFilters: 2,
        pressed: true,
      })
      await expectSnapshot('filter-button-2-filters-pressed', page)
    })
  })

  breakpoints.describeXs(({ expectSnapshot }) => {
    test('no filters applied and not scrolled', async ({ page }) => {
      await gotoWithArgs(page)
      await expectSnapshot('filter-button-no-filters-not-scrolled', page)
    })

    test('no filters but scrolled', async ({ page }) => {
      await gotoWithArgs(page, { scrolled: true })
      await expectSnapshot('filter-button-no-filters-scrolled', page)
    })

    test('2 filters not scrolled', async ({ page }) => {
      await gotoWithArgs(page, { appliedFilters: 2 })
      await expectSnapshot('filter-button-2-filters-not-scrolled', page)
    })

    test('2 filters and scrolled', async ({ page }) => {
      await gotoWithArgs(page, { appliedFilters: 2, scrolled: true })
      await expectSnapshot('filter-button-2-filters-scrolled', page)
    })
  })
})
