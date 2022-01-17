const { test, expect } = require('@playwright/test')

/**
 * Using SSR:
 * 1. Can open 'all' tab, and see Meta, image grid and Meta search form.
 * 2. Can open 'image' tab, and see Meta, image grid and Meta search form.
 * 3. Can open 'audio' tab, and see Meta, audio grid and Meta search form.
 * 4. Can open 'video' tab, and see Meta, and Meta search form.
 *
 * On client side:
 * 1. Can open 'all' tab, and see Meta, image grid and Meta search form; can load more images.
 * 2. Can open 'image' tab, and see Meta, image grid and Meta search form; can load more images.
 * 3. Can open 'audio' page, and see Meta, audio grid and Meta search form; can not (currently) load more audios.
 * 4. Can open 'video' page, and see Meta, and Meta search form; can not see load more button.
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
        headers: { 'Access-Control-Allow-Origin': '*' },
        path: 'test/e2e/resources/mock_data.json',
      })
  )
})

const contentTypes = [
  {
    id: 'all',
    name: 'All',
    url: '/search/?q=cat',
    supported: true,
    sources: 6,
  },
  {
    id: 'image',
    name: 'Images',
    url: '/search/image/?q=cat',
    supported: true,
    sources: 6,
  },
  {
    id: 'audio',
    name: 'Audio',
    url: '/search/audio/?q=cat',
    supported: false,
    sources: 5,
  },
  {
    id: 'video',
    name: 'Video',
    url: '/search/video/?q=cat',
    supported: false,
    sources: 4,
  },
]

for (const [i, contentType] of contentTypes.entries()) {
  test(`Can open ${contentType.name} search page on SSR`, async ({ page }) => {
    await page.goto(contentType.url)

    // Meta data
    if (contentType.supported) {
      const searchMetaData = await page.locator('[data-testid="search-meta"]')

      await expect(searchMetaData).toContainText(
        contentType.id === 'all' ? 'image results' : `${contentType.id} results`
      )
      await expect(searchMetaData).toContainText('Are these results relevant')
      await expect(searchMetaData).toContainText('Safer Browsing')

      const searchResult = await page.locator('[data-testid="search-results"]')
      await expect(searchResult).toBeVisible()
      await expect(searchResult).not.toBeEmpty()
    }

    // Load more
    if (contentType.supported) {
      const loadMoreBtn = await page.locator(
        'button:has-text("Load more results")'
      )
      await expect(loadMoreBtn).toHaveCount(1)
    }

    // MetaSearch form
    const metaSearchForm = await page.locator(
      '[data-testid="meta-search-form"]'
    )
    await expect(metaSearchForm).toHaveCount(1)

    const sourceButtons = await page.locator('.meta-search a')
    await expect(sourceButtons).toHaveCount(contentType.sources)
  })
  test.skip(`Can open ${contentType.name} page client-side`, async ({
    page,
  }) => {
    const pageToOpen = (i + 1) % contentTypes.length
    await page.goto(contentTypes[pageToOpen].url)

    await page.click(`[role="tab"]:has-text("${contentType.name}")`)
    const urlParam = contentType.id === 'all' ? '' : contentType.id
    const expectedURL = `/search/${urlParam}?q=cat`
    await expect(page).toHaveURL(expectedURL)

    // Selected content page
    const currentTabLabel = await page
      .locator('[aria-current="page"]')
      .textContent()

    expect(currentTabLabel.trim()).toEqual(contentType.name)

    // Meta data
    if (contentType.supported) {
      const searchMetaData = await page.locator('[data-testid="search-meta"]')

      await expect(searchMetaData).toContainText(
        contentType.id === 'all' ? 'image results' : `${contentType.id} results`
      )
      await expect(searchMetaData).toContainText('Are these results relevant')
      await expect(searchMetaData).toContainText('Safer Browsing')

      const searchResult = await page.locator('[data-testid="search-results"]')
      await expect(searchResult).toBeVisible()
      await expect(searchResult).not.toBeEmpty()
    }

    // Load more
    if (contentType.supported) {
      const loadMoreSection = await page.locator('[data-testid="load-more"]')
      await expect(loadMoreSection).toHaveCount(1)
      const expectedText =
        contentType.id === 'audio' ? 'No more audio' : 'Load more'
      await expect(loadMoreSection).toContainText(expectedText)
    } else {
      await expect(page.locator('[data-testid="load-more"]')).toHaveCount(0)
    }

    // MetaSearch form
    const metaSearchForm = await page.locator(
      '[data-testid="meta-search-form"]'
    )
    await expect(metaSearchForm).toHaveCount(1)

    const sourceButtons = await page.locator('.meta-search a')
    await expect(sourceButtons).toHaveCount(contentType.sources)
  })
}
