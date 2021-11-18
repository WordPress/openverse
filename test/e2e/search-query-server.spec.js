const { test, expect } = require('@playwright/test')

/**
 * URL is correctly converted into search state:
 * 1. `q` parameter is set as the search input value
 * 2. /search/<path>?query - path is used to choose the search tab
 * 3. query parameters are used to set the filter data:
 * 3a. One of each values for `all` tab
 * 3b. Several query values - several filter checkboxes
 * 3c. Mature filter
 * 3d. Query parameters that are not used for current media type are discarded
 * All of these tests test server-generated search page, not the one generated on the client
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
    'https://api.openverse.engineering/v1/images**',
    (route) => route.fulfill({ path: 'test/e2e/resources/mock_data.json' })
  )
})

test('q query parameter is set as the search term', async ({ page }) => {
  await page.goto(
    '/search/?q=cat&license=cc0&license_type=commercial&searchBy=creator'
  )

  const searchInput = page.locator('input[type="search"]')
  await expect(searchInput).toHaveValue('cat')
  await expect(searchInput).toBeFocused()
})

test('url path /search/ is used to select `all` search tab', async ({
  page,
}) => {
  await page.goto('/search/?q=cat')

  const activeTabLabel = await page
    .locator('[role="tab"][aria-selected="true"]')
    .textContent()
  expect(activeTabLabel.trim()).toEqual('All')
})

test('url path /search/audio is used to select `audio` search tab', async ({
  page,
}) => {
  const audioSearchUrl = '/search/audio?q=cat'
  await page.goto(audioSearchUrl)

  const activeTabLabel = await page
    .locator('[role="tab"][aria-selected="true"]')
    .textContent()
  expect(activeTabLabel.trim()).toEqual('Audio')
})

test('url query to filter, all tab, one parameter per filter type', async ({
  page,
}) => {
  await page.goto(
    '/search/?q=cat&license=cc0&license_type=commercial&searchBy=creator'
  )

  // Have to specify `aside` because there are technically two filter lists on the page:
  // aside for desktop, and a modal for mobile view.
  const cc0 = page.locator('aside input[type="checkbox"][value="cc0"]')
  await expect(cc0).toBeChecked()

  const commercial = page.locator(
    'aside input[type="checkbox"][value="commercial"]'
  )
  await expect(commercial).toBeChecked()

  // TODO (obulat): Check that this checkbox has a clear a11y name
  const searchByCreator = page.locator(
    'aside input[type="checkbox"][value="creator"]'
  )
  await expect(searchByCreator).toBeChecked()
})

test('url query to filter, image tab, several filters for one filter type selected', async ({
  page,
}) => {
  await page.goto(
    '/search/image?q=cat&searchBy=creator&extension=jpg,png,gif,svg'
  )

  const jpg = page.locator('aside input[type="checkbox"][value="jpg"]')
  await expect(jpg).toBeChecked()

  const png = page.locator('aside input[type="checkbox"][value="png"]')
  await expect(png).toBeChecked()

  const gif = page.locator('aside input[type="checkbox"][value="gif"]')
  await expect(gif).toBeChecked()

  const svg = page.locator('aside input[type="checkbox"][value="svg"]')
  await expect(svg).toBeChecked()
})

test('url mature query is set, and can be unchecked using the Safer Browsing popup', async ({
  page,
}) => {
  await page.goto('/search/image?q=cat&mature=true')

  await page.click('button:has-text("Safer Browsing")')

  const matureCheckbox = await page.locator('text=Show Mature Content')
  await expect(matureCheckbox).toBeChecked()

  await page.click('text=Show Mature Content')
  await expect(page).toHaveURL('/search/image?q=cat')
})
