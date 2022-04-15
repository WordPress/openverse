import { test, Page } from '@playwright/test'

import breakpoints from '~~/test/playwright/utils/breakpoints'
import { hideInputCursors } from '~~/test/playwright/utils/page'

const deleteImageCarousel = async (page: Page) => {
  const element = await page.$('[data-testid="image-carousel"]')
  await element?.evaluate((node) => node.remove())
  element?.dispose()
}

test.describe('homepage snapshots', () => {
  test.describe('ltr', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/')
    })

    breakpoints.describeEvery(({ expectSnapshot }) =>
      test('full page', async ({ page }) => {
        await deleteImageCarousel(page)
        await expectSnapshot('index-ltr', page)
      })
    )

    test.describe('search input', () => {
      breakpoints.describeEvery(({ expectSnapshot }) => {
        test('unfocused', async ({ page }) => {
          await expectSnapshot(
            'unfocused-search-ltr',
            page.locator('form:has(input)')
          )
        })

        test('focused', async ({ page }) => {
          await page.focus('input')
          await hideInputCursors(page)
          await expectSnapshot(
            'focused-search-ltr',
            page.locator('form:has(input)')
          )
        })
      })
    })
  })

  test.describe('rtl', () => {
    test.beforeEach(async ({ page }) => {
      await page.goto('/ar')
    })

    breakpoints.describeEvery(({ expectSnapshot }) =>
      test('full page', async ({ page }) => {
        await deleteImageCarousel(page)
        await expectSnapshot('index-rtl', page)
      })
    )

    test.describe('search input', () => {
      breakpoints.describeEvery(({ expectSnapshot }) => {
        test('unfocused', async ({ page }) => {
          await expectSnapshot(
            'unfocused-search-rtl',
            page.locator('form:has(input)')
          )
        })

        test('focused', async ({ page }) => {
          await page.focus('input')
          await hideInputCursors(page)
          await expectSnapshot(
            'focused-search-rtl',
            page.locator('form:has(input)')
          )
        })
      })
    })
  })
})
