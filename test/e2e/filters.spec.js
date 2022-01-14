const { test, expect } = require('@playwright/test')

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
  await context.route(/.+jamendo.com.+/, (route) => route.abort())

  // Replace all the thumbnail requests with a single sample image
  await context.route(
    'https://api.openverse.engineering/v1/thumbs/**',
    (route) => route.fulfill({ path: 'test/e2e/resources/sample_image.jpg' })
  )
  // Serve mock data on all image search requests
  await context.route(
    'https://api.openverse.engineering/v1/images/?***',
    (route) => route.fulfill({ path: 'test/e2e/resources/mock_data.json' })
  )
})

test('can unset filters using filter tags', async ({ page }) => {
  // Serve mock data on all image search requests
  await page.route('https://api.openverse.engineering/v1/images/?**', (route) =>
    route.fulfill({ path: 'test/e2e/resources/mock_data.json' })
  )
  await page.goto('/search/image?q=cat&license=cc0')

  const cc0Tag = page.locator('[aria-label="Remove CC0 filter"]')
  await openFilters(page)
  expect(await page.getAttribute('[aria-label="1 Filter"]', 'aria-label')).toBe(
    '1 Filter'
  )
  const cc0Checkbox = page.locator('label:has-text("CC0")')

  await expect(cc0Checkbox).toBeChecked()
  await expect(cc0Tag).toHaveCount(1)
  page.on('requestfinished', (request) => {
    const url = request.url()
    // Only check the URL for an image search query `?`, not thumbs or related requests
    const baseUrl = 'https://api.openverse.engineering/v1/images/?'
    if (url.startsWith(baseUrl)) {
      expect(url).toEqual(baseUrl + 'q=cat')
    }
  })
  await cc0Tag.click()

  await expect(page).toHaveURL('/search/image?q=cat')
  await expect(cc0Checkbox).not.toBeChecked()
  await expect(page.locator('[aria-label="Remove CC0 filter"]')).toHaveCount(0)
})

test('filters are updated when media type changes', async ({ page }) => {
  // Serve mock data on all image search requests
  await page.route('https://api.openverse.engineering/v1/images?**', (route) =>
    route.fulfill({ path: 'test/e2e/resources/mock_data.json' })
  )
  await page.goto('/search/image?q=cat&aspect_ratio=tall')
  await openFilters(page)

  const tallTag = page.locator('[aria-label="Remove Tall filter"]')
  const tallCheckbox = page.locator('label:has-text("Tall")')

  await expect(tallCheckbox).toBeChecked()
  await expect(tallTag).toHaveCount(1)

  await page.click('[role="tab"]:has-text("Audio")')

  // TODO(obulat): the URL should not have aspect_ratio query for audio
  // await expect(page).toHaveURL('/search/audio/?q=cat')
  await expect(page).toHaveURL('/search/audio?q=cat&aspect_ratio=tall')

  await expect(tallTag).toHaveCount(0)
  await expect(tallCheckbox).toHaveCount(0)
})

test('new media request is sent when a filter is selected', async ({
  page,
}) => {
  let apiRequest
  // Serve mock data on all image search requests and save the API request url
  // There must be a better way to get the request url than this
  await page.route(
    'https://api.openverse.engineering/v1/images/?**',
    (route) => {
      apiRequest = route.request().url()
      route.fulfill({ path: 'test/e2e/resources/mock_data.json' })
    }
  )
  await page.goto('/search/image?q=cat')
  await openFilters(page)

  const cc0Checkbox = page.locator('label:has-text("CC0")')
  await expect(cc0Checkbox).not.toBeChecked()
  await cc0Checkbox.click()

  await expect(cc0Checkbox).toBeChecked()
  await expect(apiRequest).toEqual(
    'https://api.openverse.engineering/v1/images/?q=cat&license=cc0'
  )
})
