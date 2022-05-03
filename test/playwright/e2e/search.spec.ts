/**
 * Shows Search Grid / search meta information (count, etc.)
 * On clicking 'Load More', requests the same URL with the additional
 * `page=page+1` parameter
 * When finished, shows 'No more images'
 * When pending: does not show 'No images', Safer Browsing, search rating or error message
 * On error: shows error message
 */
import { expect, test } from '@playwright/test'

import { mockProviderApis } from '~~/test/playwright/utils/route'

test.beforeEach(async ({ context }) => {
  await mockProviderApis(context)
})

test('shows no results page when no results', async ({ page }) => {
  await page.goto('/search/image?q=243f6a8885a308d3')
  await expect(page.locator('.error-section')).toBeVisible()
})
