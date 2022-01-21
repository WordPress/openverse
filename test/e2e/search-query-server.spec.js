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

const openFilters = async (page) => {
  const filterButtonSelector =
    '[aria-controls="filter-sidebar"], [aria-controls="filter-modal"]'
  const isPressed = async () =>
    await page.getAttribute(filterButtonSelector, 'aria-pressed')
  if ((await isPressed()) !== 'true') {
    await page.click(filterButtonSelector)
    expect(await isPressed()).toEqual('true')
  }
}

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
  await page.goto(
    '/search/?q=cat&license=cc0&license_type=commercial&searchBy=creator'
  )

  const searchInput = page.locator('input[type="search"]')
  await expect(searchInput).toHaveValue('cat')
  // Todo: focus the input?
  // await expect(searchInput).toBeFocused()
})

test.skip('url path /search/ is used to select `all` search tab', async ({
  page,
}) => {
  await page.goto('/search/?q=cat')

  const activeTabLabel = await page
    .locator('[role="tab"][aria-selected="true"]')
    .textContent()
  expect(activeTabLabel.trim()).toEqual('All')
})

test.skip('url path /search/audio is used to select `audio` search tab', async ({
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

  await openFilters(page)
  const cc0Checkbox = await page.locator('label:has-text("CC0")')
  await expect(cc0Checkbox).toBeChecked()

  const commercial = await page.locator('label:text-matches("commercial", "i")')
  await expect(commercial).toBeChecked()

  const searchByCreator = await page.locator('label:has-text("Creator")')
  await expect(searchByCreator).toBeChecked()
})

test('url query to filter, image tab, several filters for one filter type selected', async ({
  page,
}) => {
  await page.goto(
    '/search/image?q=cat&searchBy=creator&extension=jpg,png,gif,svg'
  )
  await openFilters(page)

  const jpeg = page.locator('label:text-matches("jp(e*)g", "i")')
  await expect(jpeg).toBeChecked()

  const png = page.locator('label:text-matches("png", "i")')
  await expect(png).toBeChecked()

  const gif = page.locator('label:text-matches("gif", "i")')
  await expect(gif).toBeChecked()

  const svg = page.locator('label:text-matches("svgs", "i")')
  await expect(svg).toBeChecked()
})

test.skip('url mature query is set, and can be unchecked using the Safer Browsing popup', async ({
  page,
}) => {
  await page.goto('/search/image?q=cat&mature=true')

  await page.click('button:has-text("Safer Browsing")')

  const matureCheckbox = await page.locator('text=Show Mature Content')
  await expect(matureCheckbox).toBeChecked()

  await page.click('text=Show Mature Content')
  await expect(page).toHaveURL('/search/image?q=cat')
})
