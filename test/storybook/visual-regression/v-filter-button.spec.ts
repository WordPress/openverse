import { test } from '@playwright/test'

import breakpoints from '~~/test/playwright/utils/breakpoints'
import { makeGotoWithArgs } from '~~/test/storybook/utils/args'

const gotoWithArgs = makeGotoWithArgs(
  'components-vheader-vfilterbutton--default-story'
)

test.describe.configure({ mode: 'parallel' })

test.describe('VFilterButton', () => {
  breakpoints.describeLg(({ expectSnapshot }) => {
    test('no filters applied', async ({ page }) => {
      await gotoWithArgs(page, { isMinMd: true })
      await expectSnapshot('filter-button-at-rest', page)
    })

    test('no filters pressed', async ({ page }) => {
      await gotoWithArgs(page, { pressed: true })
      await expectSnapshot('filter-button-pressed', page)
    })

    test('filters applied', async ({ page }) => {
      await gotoWithArgs(page, { appliedFilters: 2 })
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

  breakpoints.describeXl(({ expectSnapshot }) => {
    test('no filters applied', async ({ page }) => {
      await gotoWithArgs(page)
      await expectSnapshot('filter-button-no-filters-not-scrolled', page)
    })

    test('2 filters', async ({ page }) => {
      await gotoWithArgs(page, { appliedFilters: 2 })
      await expectSnapshot('filter-button-2-filters-not-scrolled', page)
    })
  })
})
