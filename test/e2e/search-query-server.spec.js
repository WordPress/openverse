const { test, expect } = require('@playwright/test')
const { mockAllSearch, openFilters } = require('./utils')
const { currentContentType, assertCheckboxCheckedStatus } = require('./utils')

/**
 * URL is correctly converted into search state:
 * 1. `q` parameter is set as the search input value
 * 2. /search/<path>?query - path is used to choose the content type
 * 3. query parameters are used to set the filter data:
 * 3a. One of each values for `all` content
 * 3b. Several query values - several filter checkboxes
 * 3c. Mature filter
 * 3d. Query parameters that are not used for current media type are discarded
 * All of these tests test server-generated search page, not the one generated on the client
 */

test.beforeEach(async ({ context }) => {
  // Block any image or audio (jamendo.com) requests for each test in this file.
  await context.route('**.jamendo.com**', (route) => route.abort())
  await mockAllSearch(context)
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

test('url path /search/ is used to select `all` search tab', async ({
  page,
}) => {
  await page.goto('/search/?q=cat')

  const contentType = await currentContentType(page)
  expect(contentType.trim()).toEqual('All content')
})

test('url path /search/audio is used to select `audio` search tab', async ({
  page,
}) => {
  const audioSearchUrl = '/search/audio?q=cat'
  await page.goto(audioSearchUrl)

  const contentType = await currentContentType(page)
  expect(contentType.trim()).toEqual('Audio')
})

test('url query to filter, all tab, one parameter per filter type', async ({
  page,
}) => {
  await page.goto(
    '/search/?q=cat&license=cc0&license_type=commercial&searchBy=creator'
  )

  await openFilters(page)
  await assertCheckboxCheckedStatus(page, 'cc0')
  await assertCheckboxCheckedStatus(page, 'commercial')
  await assertCheckboxCheckedStatus(page, 'creator')
})

test('url query to filter, image tab, several filters for one filter type selected', async ({
  page,
}) => {
  await page.goto(
    '/search/image?q=cat&searchBy=creator&extension=jpg,png,gif,svg'
  )
  await openFilters(page)
  const checkboxes = ['jpeg', 'png', 'gif', 'svgs']
  for (let checkbox of checkboxes) {
    await assertCheckboxCheckedStatus(page, checkbox)
  }
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
