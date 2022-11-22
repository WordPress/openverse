import { test } from '@playwright/test'

import { removeHiddenOverflow } from '~~/test/playwright/utils/page'
import breakpoints from '~~/test/playwright/utils/breakpoints'
import {
  closeFilters,
  dismissTranslationBanner,
  enableNewHeader,
  goToSearchTerm,
  isPageDesktop,
  languageDirections,
  openFirstResult,
} from '~~/test/playwright/utils/navigation'

import { supportedMediaTypes } from '~/constants/media'

test.describe.configure({ mode: 'parallel' })

for (const mediaType of supportedMediaTypes) {
  for (const dir of languageDirections) {
    test.describe(`${mediaType} ${dir} single-result page snapshots`, () => {
      breakpoints.describeEvery(({ expectSnapshot }) => {
        test.beforeEach(async ({ page }) => {
          await enableNewHeader(page)
          await goToSearchTerm(page, 'birds', { dir })
          if (isPageDesktop(page)) await closeFilters(page)
          await dismissTranslationBanner(page)
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
