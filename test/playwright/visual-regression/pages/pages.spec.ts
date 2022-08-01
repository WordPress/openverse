import { test } from '@playwright/test'

import breakpoints from '~~/test/playwright/utils/breakpoints'
import { removeHiddenOverflow } from '~~/test/playwright/utils/page'
import {
  dismissTranslationBanner,
  pathWithDir,
  languageDirections,
} from '~~/test/playwright/utils/navigation'

test.describe.configure({ mode: 'parallel' })

const contentPages = [
  'extension',
  'about',
  'meta-search',
  'search-help',
  'non-existent',
]
for (const contentPage of contentPages) {
  for (const dir of languageDirections) {
    test.describe(`${contentPage} ${dir} page snapshots`, () => {
      test.beforeEach(async ({ page }) => {
        await page.goto(pathWithDir(contentPage, dir))
        await dismissTranslationBanner(page)
      })

      breakpoints.describeEvery(({ expectSnapshot }) => {
        test('full page', async ({ page }) => {
          await removeHiddenOverflow(page)
          // Make sure header is not hovered on
          await page.mouse.move(150, 150)
          await expectSnapshot(`${contentPage}-${dir}`, page, {
            fullPage: true,
          })
        })
      })
    })
  }
}
