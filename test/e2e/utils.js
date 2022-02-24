const { expect } = require('@playwright/test')

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

const assertCheckboxCheckedStatus = async (page, label, checked = true) => {
  const checkbox = page.locator(`label:has-text("${label}")`)
  if (checked) {
    await expect(checkbox).toBeChecked()
  } else {
    await expect(checkbox).not.toBeChecked()
  }
}

/**
 * Replace all the thumbnail requests with a single sample image
 */
const mockThumbnails = async (context) => {
  await context.route(
    'https://api.openverse.engineering/v1/thumbs/**',
    (route) =>
      route.fulfill({
        path: 'test/e2e/resources/sample_image.jpg',
        headers: { 'Access-Control-Allow-Origin': '*' },
      })
  )
}
/**
 * Replace all the image search requests with mock data
 */
const mockImageSearch = async (context) => {
  // Serve mock data on all image search requests
  await context.route(
    'https://api.openverse.engineering/v1/images/?***',
    (route) =>
      route.fulfill({
        path: 'test/e2e/resources/mock_image_data.json',
        headers: { 'Access-Control-Allow-Origin': '*' },
      })
  )
}
/**
 * Replace all the image search requests with mock data
 */
const mockAudioSearch = async (context) => {
  // Serve mock data on all image search requests
  await context.route(
    'https://api.openverse.engineering/v1/audio/?***',
    (route) =>
      route.fulfill({
        path: 'test/e2e/resources/mock_audio_data.json',
        headers: { 'Access-Control-Allow-Origin': '*' },
      })
  )
}
const mockImages = async (context) => {
  await context.route(/\.(png|jpeg|jpg|svg)$/, (route) => route.abort())
}

const changeContentType = async (page, to) => {
  await page.click(
    `button[aria-controls="content-switcher-popover"], button[aria-controls="content-switcher-modal"]`
  )
  await page.click(`button[role="radio"]:has-text("${to}")`)
}
/**
 * Finds a button with a popup to the left of the filters button which doesn't have a 'menu' label
 * @param page
 * @returns {Promise<string>}
 */
const currentContentType = async (page) => {
  const contentSwitcherButton = await page.locator(
    `button[aria-controls="content-switcher-popover"], button[aria-controls="content-switcher-modal"]`
  )
  return contentSwitcherButton.textContent()
}

const mockAllSearch = async (context) => {
  await Promise.all([
    mockAudioSearch(context),
    mockImageSearch(context),
    mockThumbnails(context),
    mockImages(context),
  ])
}

module.exports = {
  openFilters,
  changeContentType,
  currentContentType,
  assertCheckboxCheckedStatus,
  mockAllSearch,
  mockThumbnails,
  mockImages,
}
