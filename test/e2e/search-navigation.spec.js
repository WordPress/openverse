const { expect, test } = require('@playwright/test')

const { openFilters } = require('./utils')

test.beforeEach(async ({ context }) => {
  await context.route('**.jamendo.**', (r) => r.abort())
  await context.route('**.freesound.**', (r) => r.abort())
})

test.describe('search history navigation', () => {
  test('should update search results when back navigation changes filters', async ({
    page,
  }) => {
    await page.goto('/search/?q=galah')
    // Open filter sidebar
    await openFilters(page)

    // Apply a filter
    await page.click('#modification')

    // Verify the filter is appled to the URL and the checkbox is checked
    // Note: Need to add that a search was actually executed with the new
    // filters and that the page results have been updated for the new filters
    // @todo(sarayourfriend): ^?
    expect(page.url()).toContain('license_type=modification')
    expect(await page.isChecked('#modification')).toBe(true)

    // Navigate backwards and verify URL is updated and the filter is unapplied
    await page.goBack()

    // Ditto here about the note above, need to verify a new search actually happened with new results
    expect(page.url()).not.toContain('license_type=modification')
    expect(await page.isChecked('#modification')).toBe(false)
  })

  test('should update search results when back button updates search type', async ({
    page,
  }) => {
    await page.goto('/search?q=galah')
    await page.click('text=See all images')
    await page.waitForSelector('text=See all images', { state: 'hidden' })
    expect(page.url()).toContain('/search/image')
    await page.goBack()
    await page.waitForSelector('text=See all images')
    expect(await page.locator('text=See all images').isVisible()).toBe(true)
    expect(await page.locator('text=See all audio').isVisible()).toBe(true)
  })
})
