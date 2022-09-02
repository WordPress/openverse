import { test, expect } from '@playwright/test'

import {
  goToSearchTerm,
  languageDirections,
} from '~~/test/playwright/utils/navigation'

import { supportedSearchTypes } from '~/constants/media'

test.describe.configure({ mode: 'parallel' })

for (const dir of languageDirections) {
  for (const searchType of supportedSearchTypes) {
    test(`External ${searchType} sources popover - ${dir}`, async ({
      page,
    }) => {
      await goToSearchTerm(page, 'birds', { searchType, dir })
      const externalSourcesButton = page.locator(
        '[aria-controls="source-list-popover"]'
      )

      await externalSourcesButton.click()

      expect(
        await page.locator('[data-testid="source-list-popover"]').screenshot()
      ).toMatchSnapshot({
        name: `external-${searchType}-sources-popover-${dir}.png`,
      })
    })
  }
}
