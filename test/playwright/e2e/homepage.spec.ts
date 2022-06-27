import { test, expect } from '@playwright/test'

import { mockProviderApis } from '~~/test/playwright/utils/route'
import {
  goToSearchTerm,
  searchTypePath,
} from '~~/test/playwright/utils/navigation'

import { supportedSearchTypes } from '~/constants/media'

test.beforeEach(async ({ context }) => {
  await mockProviderApis(context)
})

for (const searchType of supportedSearchTypes) {
  test(`can change type and search for ${searchType} from homepage`, async ({
    page,
  }) => {
    await goToSearchTerm(page, 'cat', { searchType, mode: 'CSR' })

    const expectedUrl = `/search/${searchTypePath(searchType)}?q=cat`
    await expect(page).toHaveURL(expectedUrl)
  })
}
