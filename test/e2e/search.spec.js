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

test.skip('shows search result metadata', async ({ page }) => {
  await page.goto('/search/image?q=cat&source=rijksmuseum')
  await page.route('https://api.openverse.engineering/v1/images/**', (route) =>
    route.fulfill({ path: 'test/e2e/resources/last_page.json' })
  )

  // Expect results meta
  // Flaky test. Is there a way to mock the first api result when loading on the server?
  await expect(page.locator('.results-meta span.pe-6')).toContainText(
    /image results/
  )
  await expect(page.locator('text=Are these results relevant?')).toHaveCount(1)

  // Click load more button
  const loadMoreButton = page.locator('button:has-text("Load more results")')
  await expect(loadMoreButton).toHaveCount(1)
  await loadMoreButton.click()

  // Click load more button
  await expect(loadMoreButton).toHaveCount(1)
  await loadMoreButton.click()
  // All search results have been shown, cannot load more
  await expect(loadMoreButton).toHaveCount(0)
})

test('navigates to the image detail page correctly', async ({ page }) => {
  await page.goto('/search/image?q=honey')
  const figure = page.locator('figure').first()
  const imgTitle = await figure.locator('img').getAttribute('alt')

  await page.locator('figure a').first().click()
  // Until the image is loaded, the heading is 'Image' instead of the actual title

  const headingText = await page.locator('h1').textContent()
  expect(headingText.trim().toLowerCase()).toEqual(imgTitle.toLowerCase())
  // Renders the breadcrumb link
  await expect(page.locator('text="Back to search results"')).toBeVisible()
})

test('the Back to search results link returns to the search page', async ({
  page,
}) => {
  const url = '/search/image?q=honey'
  await page.goto(url)
  await page.locator('figure a').first().click()
  await page.locator('text="Back to search results"').click()
  await expect(page).toHaveURL(url)
})
