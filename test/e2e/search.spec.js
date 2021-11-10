/**
 * Shows Search Grid / search meta information (count, etc.)
 * On clicking 'Load More', requests the same URL with the additional
 * `page=page+1` parameter
 * When finished, shows 'No more images'
 * When pending: does not show 'No images', Safer Browsing, search rating or error message
 * On error: shows error message
 */
const { expect, test } = require('@playwright/test')
test.beforeEach(async ({ context }) => {
  // Block any image or audio (jamendo.com) requests for each test in this file.
  await context.route(/\.(png|jpeg|jpg|svg)$/, (route) => route.abort())
  await context.route('**.jamendo.com**', (route) => route.abort())

  // Replace all the thumbnail requests with a single sample image
  await context.route(
    'https://api.openverse.engineering/v1/thumbs/**',
    (route) => route.fulfill({ path: 'test/e2e/resources/sample_image.jpg' })
  )
})

// TODO(obulat): Fix the search metadata before search
//  This test currently passes, although everything should be the opposite
test('does not show an error message before search', async ({ page }) => {
  await page.goto('/search')

  // The search meta data under the search input, should not be shown if no
  // media had been fetched
  await expect(page.locator('span:has-text("No image results")')).toHaveCount(1)

  // Load more button, should not be shown if the `q` parameter is not set
  await expect(page.locator('button:has-text("Load more results")'))

  // There should be no error messages when no search has been done
  await expect(page.locator('[data-testid="search-grid"] h4')).toHaveCount(1)
  await expect(page.locator('text=No image results for')).toHaveCount(1)
})

test('shows search result metadata', async ({ page }) => {
  await page.goto('/search/image?source=rijksmuseum&q=cat')
  await page.route('https://api.openverse.engineering/v1/images/**', (route) =>
    route.fulfill({ path: 'test/e2e/resources/last_page.json' })
  )

  // Expect results meta
  // Flaky test. Is there a way to mock the first api result?
  await expect(page.locator('text=41 image results')).toHaveCount(1)
  await expect(page.locator('text=Are these results relevant?')).toHaveCount(1)

  // Click load more button
  const loadMoreButton = page.locator('button:has-text("Load more results")')
  await expect(loadMoreButton).toHaveCount(1)
  await loadMoreButton.click()

  // All search results have been shown, cannot load more
  await expect(loadMoreButton).toHaveCount(0)
})
