const { test, expect } = require('@playwright/test')

test.beforeEach(async ({ context }) => {
  // Block any image or audio (jamendo.com) requests for each test in this file.
  await context.route(/\.(png|jpeg|jpg|svg)$/, (route) => route.abort())

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
        path: 'test/e2e/resources/mock_image_data.json',
        headers: { 'Access-Control-Allow-Origin': '*' },
      })
  )
})

test('can change type and search for audio from homepage', async ({ page }) => {
  // Go to http://localhost:8444/
  await page.goto('/')
  await page.click('[aria-label="All content"]')
  await page.click('button[role="radio"]:has-text("Audio")')

  const searchInput = page.locator('main input[type="search"]')
  await searchInput.type('cat')
  await page.click('[aria-label="Search"]')
  const expectedUrl = '/search/audio?q=cat'
  await expect(page).toHaveURL(expectedUrl)
})

test('can search for all results from homepage', async ({ page }) => {
  await page.goto('/')

  const searchInput = page.locator('main input[type="search"]')
  await searchInput.type('cat')
  await page.click('[aria-label="Search"]')

  await expect(page).toHaveURL('search/?q=cat')

  await expect(page.locator('img')).toHaveCount(20)
})
test('can search for images from homepage', async ({ page }) => {
  await page.goto('/')
  await page.click('[aria-label="All content"]')
  await page.click('button[role="radio"]:has-text("Images")')

  const searchInput = page.locator('main input[type="search"]')
  await searchInput.type('cat')
  await page.click('[aria-label="Search"]')

  await expect(page).toHaveURL('search/image?q=cat')

  await expect(page.locator('img')).toHaveCount(20)
})
