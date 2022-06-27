import { test } from '@playwright/test'

import breakpoints from '~~/test/playwright/utils/breakpoints'
import { hideInputCursors } from '~~/test/playwright/utils/page'
import {
  goToSearchTerm,
  languageDirections,
  scrollToBottom,
  sleep,
} from '~~/test/playwright/utils/navigation'

const headerSelector = '.main-header'
const loadMoreSelector = 'button:has-text("Load more")'

test.describe('header snapshots', () => {
  for (const dir of languageDirections) {
    test.describe(dir, () => {
      test.beforeEach(async ({ page }) => {
        await goToSearchTerm(page, 'birds', { dir: dir })
      })

      test.describe('header', () => {
        breakpoints.describeEvery(({ expectSnapshot }) => {
          test('resting', async ({ page }) => {
            await expectSnapshot(`resting-${dir}`, page.locator(headerSelector))
          })

          test('scrolled', async ({ page }) => {
            await page.locator(loadMoreSelector).focus()
            await scrollToBottom(page)
            await sleep(200)
            await expectSnapshot(
              `scrolled-${dir}`,
              page.locator(headerSelector)
            )
          })

          test('searchbar hovered', async ({ page }) => {
            await page.hover('input')
            await hideInputCursors(page)
            await expectSnapshot(
              `searchbar-hovered-${dir}`,
              page.locator(headerSelector)
            )
          })
        })
      })
    })
  }
})
