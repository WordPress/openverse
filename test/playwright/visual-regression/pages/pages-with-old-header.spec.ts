import { test } from '@playwright/test'

import breakpoints from '~~/test/playwright/utils/breakpoints'
import { removeHiddenOverflow } from '~~/test/playwright/utils/page'
import {
  dismissTranslationBanner,
  pathWithDir,
  languageDirections,
} from '~~/test/playwright/utils/navigation'

test.describe.configure({ mode: 'parallel' })

const contentPages = ['about', 'search-help', 'non-existent', 'sources']
for (const contentPage of contentPages) {
  for (const dir of languageDirections) {
    test.describe(`${contentPage} ${dir} page snapshots`, () => {
      breakpoints.describeEvery(({ breakpoint, expectSnapshot }) => {
        test('full page', async ({ page }) => {
          await page.context().addCookies([
            {
              name: 'uiBreakpoint',
              value: JSON.stringify(breakpoint),
              domain: 'localhost',
              path: '/',
            },
          ])
          await page.goto(pathWithDir(contentPage, dir))
          await dismissTranslationBanner(page)

          await removeHiddenOverflow(page)
          // Make sure header is not hovered on
          await page.mouse.move(150, 150)
          await page.waitForLoadState('networkidle')
          await expectSnapshot(`${contentPage}-${dir}`, page, {
            fullPage: true,
          })
        })
      })
    })
  }
}
