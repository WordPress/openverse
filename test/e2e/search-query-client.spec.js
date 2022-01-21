const { test, expect } = require('@playwright/test')

/**
 * When navigating to the search page on the client side:
 * 1. `q` parameter is set as the search input value and url parameter.
 * 2. Selecting 'audio' on homepage sets the search page path and search tab.
 * 3. Selecting filters on the homepage sets the search query and url parameter.
 * 4. Query parameters (filter types or filter values) that are not used for
 * current media type are discarded.
 * 5. Can change the `q` parameter by typing into the search input and clicking on
 * the Search button.
 * All of these tests test search page on the client
 */

test.beforeEach(async ({ context }) => {
  // Block any image or audio (jamendo.com) requests for each test in this file.
  await context.route(/\.(png|jpeg|jpg|svg)$/, (route) => route.abort())
  await context.route('**.jamendo.com**', (route) => route.abort())

  // Replace all the thumbnail requests with a single sample image
  await context.route(
    'https://api.openverse.engineering/v1/thumbs/**',
    (route) => route.fulfill({ path: 'test/e2e/resources/sample_image.jpg' })
  )
  // Serve mock data on all image search requests
  await context.route(
    'https://api.openverse.engineering/v1/images/**',
    (route) =>
      route.fulfill({
        path: 'test/e2e/resources/mock_data.json',
        headers: { 'Access-Control-Allow-Origin': '*' },
      })
  )
})

test('q query parameter is set as the search term', async ({ page }) => {
  await page.goto('/')

  const searchInput = page.locator('main input[type="search"]')
  await searchInput.type('cat')
  await page.click('[aria-label="Search"]')

  await expect(page.locator('header input[type="search"]')).toHaveValue('cat')
  await expect(page).toHaveURL('search/?q=cat')
})

test('selecting `audio` on homepage, you can search for audio', async ({
  page,
}) => {
  await page.goto('/')
  await page.click('[aria-label="All content"]')
  await page.click('button[role="radio"]:has-text("Audio")')

  await page.type('main input[type="search"]', 'cat')
  await page.click('[aria-label="Search"]')

  await expect(page.locator('header input[type="search"]')).toHaveValue('cat')

  await expect(page).toHaveURL('search/audio?q=cat')
})

test.skip('url filter parameters not used by current mediaType are discarded', async ({
  page,
}) => {
  // TODO(obulat): Discard unused filter parameters for mediaType
  // Some filter types have different possible values for different media types.
  // For example, image has 'photograph' category, but audio doesn't (but it has
  // 'music', 'sound'). On switching the media type when clicking on another
  // search tab, such filters should be reset, and the query should be updated.
  await page.goto('/search/image?q=cat&categories=photograph')

  await page.click('[role="tab"]:has-text("Audio")')
  await expect(page).toHaveURL('/search/audio?q=cat')
})

test.skip('url filter types not used by current mediaType are discarded', async ({
  page,
}) => {
  // TODO(obulat): Discard unused filter types for mediaType
  // Some filter types only apply to one media type. On switching the media type
  // when clicking on another search tab, such filters should be reset,
  // and the query should be updated.
  await page.goto('/search/image?q=cat&aspect_ratio=tall')

  await page.click('[role="tab"]:has-text("Audio")')
  await expect(page).toHaveURL('/search/audio?q=cat')
})

test('can search for a different term', async ({ page }) => {
  await page.goto('/search/image?q=cat')
  await page.fill('header input[type="search"]', 'dog')
  await page.keyboard.press('Enter')
  await expect(page).toHaveURL('/search/image?q=dog')
})

test('search for a different term keeps query parameters', async ({ page }) => {
  await page.goto('/search/image?q=cat&license=by&extension=jpg')
  await page.fill('header input[type="search"]', 'dog')
  await page.keyboard.press('Enter')
  await expect(page).toHaveURL('/search/image?q=dog&license=by&extension=jpg')
})
