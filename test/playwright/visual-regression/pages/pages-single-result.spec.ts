import { test } from '@playwright/test'

import { removeHiddenOverflow } from '~~/test/playwright/utils/page'
import breakpoints from '~~/test/playwright/utils/breakpoints'
import {
  enableNewHeader,
  goToSearchTerm,
  languageDirections,
  openFirstResult,
  setCookies,
} from '~~/test/playwright/utils/navigation'

import { supportedMediaTypes } from '~/constants/media'

test.describe.configure({ mode: 'parallel' })

for (const mediaType of supportedMediaTypes) {
  for (const dir of languageDirections) {
    test.describe(`${mediaType} ${dir} single-result page snapshots`, () => {
      breakpoints.describeEvery(({ breakpoint, expectSnapshot }) => {
        test.beforeEach(async ({ context, page }) => {
          await enableNewHeader(page)
          await setCookies(context, {
            uiBreakpoint: breakpoint,
            uiIsFilterDismissed: true,
            uiDismissedBanners: ['translation-ar'],
          })
          await goToSearchTerm(page, 'birds', { dir })
        })

        test(`from search results`, async ({ page }) => {
          // This will include the "Back to results" link.
          await openFirstResult(page, mediaType)
          await removeHiddenOverflow(page)
          await expectSnapshot(
            `${mediaType}-${dir}-from-search-results`,
            page,
            { fullPage: true }
          )
        })
      })
    })
  }
}
