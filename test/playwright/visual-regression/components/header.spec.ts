import { test } from '@playwright/test'

import breakpoints from '~~/test/playwright/utils/breakpoints'
import { hideInputCursors } from '~~/test/playwright/utils/page'

const headerSelector = '.main-header'
const loadMoreSelector = 'button:has-text("Load more")'

test.describe('header snapshots', () => {
  test.describe('ltr', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/search/?q=birds')
    })

    test.describe('header', () => {
      breakpoints.describeEvery(({ expectSnapshot }) => {
        test('resting', async ({ page }) => {
          await expectSnapshot('resting-ltr', page.locator(headerSelector))
        })

        test('scrolled', async ({ page }) => {
          await page.locator(loadMoreSelector).focus()
          await expectSnapshot('scrolled-ltr', page.locator(headerSelector))
        })

        test('searchbar hovered', async ({ page }) => {
          await page.hover('input')
          await hideInputCursors(page)
          await expectSnapshot(
            'searchbar-hovered-ltr',
            page.locator(headerSelector)
          )
        })
      })
    })
  })

  test.describe('rtl', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/ar/search/?q=birds')
    })

    test.describe('header', () => {
      breakpoints.describeEvery(({ expectSnapshot }) => {
        test('resting', async ({ page }) => {
          await expectSnapshot('resting-rtl', page.locator(headerSelector))
        })

        test('scrolled', async ({ page }) => {
          await page.locator(loadMoreSelector).focus()
          await page.mouse.wheel(10, 0)
          await expectSnapshot('scrolled-rtl', page.locator(headerSelector))
        })

        test('searchbar hovered', async ({ page }) => {
          await page.hover('input')
          await hideInputCursors(page)
          await expectSnapshot(
            'searchbar-hovered-rtl',
            page.locator(headerSelector)
          )
        })
      })
    })
  })
})
