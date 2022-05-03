import { expect, test } from '@playwright/test'

import { openFilters } from '~~/test/playwright/utils/navigation'
import { mockProviderApis } from '~~/test/playwright/utils/route'

test.beforeEach(async ({ context }) => {
  mockProviderApis(context)
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

test('navigates to the image detail page correctly', async ({ page }) => {
  await page.goto('/search/image?q=honey')
  const figure = page.locator('figure').first()
  const imgTitle = await figure.locator('img').getAttribute('alt')

  await page.locator('a[href^="/image"]').first().click()
  // Until the image is loaded, the heading is 'Image' instead of the actual title
  await page.locator('#main-image').waitFor()

  const headingText = await page.locator('h1').textContent()
  expect(headingText?.trim().toLowerCase()).toEqual(imgTitle?.toLowerCase())
})

test.describe('back to search results link', () => {
  test('is visible in breadcrumb when navigating to image details page and returns to the search page', async ({
    page,
  }) => {
    const url = '/search/?q=galah'
    await page.goto(url)
    await page.locator('a[href^="/image"]').first().click()
    const link = page.locator('text="Back to search results"')
    await expect(link).toBeVisible()
    await link.click()
    await expect(page).toHaveURL(url)
  })

  test('is visible in breadcrumb when navigating to localized image details page', async ({
    page,
  }) => {
    await page.goto('/es/search/?q=galah')
    await page.locator('a[href^="/es/image"]').first().click()
    await expect(
      page.locator('text="Volver a los resultados de búsqueda"')
    ).toBeVisible()
  })

  test('is visible in breadcrumb when navigating to localized audio details page', async ({
    page,
  }) => {
    await page.goto('/es/search/?q=galah')
    await page.locator('a[href^="/es/audio"]').first().click()
    await expect(
      page.locator('text="Volver a los resultados de búsqueda"')
    ).toBeVisible()
  })
})
