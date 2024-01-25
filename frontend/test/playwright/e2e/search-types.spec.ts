import { test, expect, Page } from "@playwright/test"

import {
  changeSearchType,
  goToSearchTerm,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"
import { mockProviderApis } from "~~/test/playwright/utils/route"
import breakpoints from "~~/test/playwright/utils/breakpoints"

import { searchPath } from "~/constants/media"

/**
 * Using SSR:
 * 1. Can open 'all content' search page, and see search results.
 * 2. Can open 'image' search page, and see search results.
 * 3. Can open 'audio' content type page, and see search results.
 *
 * On client side:
 * 1. Can open 'all content' search page, and see search results.
 * 2. Can open 'image' search page, and see search results.
 * 3. Can open 'audio' search page, and see search results.
 * 4. Can open 'image' search page from the 'all content' page.
 * 5. Can open 'audio' search from the 'all content' page.
 *
 * Results include search meta information, media grid and Meta search form, can load more media if there are more media items.
 */

test.describe.configure({ mode: "parallel" })

const allContentConfig = {
  id: "all",
  name: "All content",
  url: "/search?q=birds",
  canLoadMore: true,
} as const

const imageConfig = {
  id: "image",
  name: "Images",
  url: "/search/image?q=birds",
  canLoadMore: true,
  results: /Over 10,000 results/,
} as const

const audioConfig = {
  id: "audio",
  name: "Audio",
  url: "/search/audio?q=birds",
  canLoadMore: true,
  results: /Over 10,000 results/,
} as const

const searchTypes = [allContentConfig, imageConfig, audioConfig] as const

type SearchTypeConfig = (typeof searchTypes)[number]

async function checkLoadMore(page: Page, searchType: SearchTypeConfig) {
  const loadMoreSection = page.locator('[data-testid="load-more"]')
  if (!searchType.canLoadMore) {
    // When we expect the section not to be here, the test becomes very slow because
    // it waits until the end of the timeout (5 seconds).
    await expect(loadMoreSection).toHaveCount(0, { timeout: 300 })
  } else {
    await expect(loadMoreSection).toHaveCount(1)
    await expect(loadMoreSection).toContainText("Load more")
  }
}
async function checkExternalSourcesForm(page: Page) {
  await expect(
    page.locator('[data-testid="external-sources-form"]')
  ).toBeVisible()
}

async function checkSearchMetadata(page: Page, searchType: SearchTypeConfig) {
  if (searchType.canLoadMore) {
    const searchResult = page.locator('[data-testid="search-results"]')
    await expect(searchResult).toBeVisible()
    await expect(searchResult).not.toBeEmpty()
  }
}

async function checkPageMeta(page: Page, searchType: SearchTypeConfig) {
  // const expectedTitle = `birds | Openverse`
  const expectedURL = `${searchPath(searchType.id)}?q=birds`

  // await expect(page).toHaveTitle(expectedTitle)
  await expect(page).toHaveURL(expectedURL)
}

/* eslint playwright/expect-expect: ["warn", { "additionalAssertFunctionNames": ["checkSearchResult"] }] */
async function checkSearchResult(page: Page, searchType: SearchTypeConfig) {
  await checkSearchMetadata(page, searchType)
  await checkLoadMore(page, searchType)
  await checkPageMeta(page, searchType)
  if (searchType.id !== "all") {
    await checkExternalSourcesForm(page)
  }
}

test.describe("search types", () => {
  breakpoints.describeMobileAndDesktop(({ breakpoint }) => {
    test.beforeEach(async ({ context, page }) => {
      await mockProviderApis(context)
      await preparePageForTests(page, breakpoint, {
        features: { fetch_sensitive: "off", fake_sensitive: "off" },
      })
    })

    for (const searchType of searchTypes) {
      test(`Can open ${searchType.name} search page on SSR`, async ({
        page,
      }) => {
        await goToSearchTerm(page, "birds", { searchType: searchType.id })

        await checkSearchResult(page, searchType)
      })

      test(`Can open ${searchType.name} page client-side`, async ({ page }) => {
        // Audio is loading a lot of files, so we do not use it for the first SSR page
        const pageToOpen =
          // eslint-disable-next-line playwright/no-conditional-in-test
          searchType.id === "all" ? searchTypes[1] : searchTypes[0]
        await page.goto(pageToOpen.url)
        await changeSearchType(page, searchType.id)
        await checkSearchResult(page, searchType)
      })
    }

    for (const searchTypeName of ["audio", "image"] as const) {
      const searchType = searchTypes.find(
        (type) => type.id === searchTypeName
      ) as typeof audioConfig | typeof imageConfig
      test(`Can open ${searchTypeName} page from the all view`, async ({
        page,
      }) => {
        await goToSearchTerm(page, "birds")
        const contentLink = page.locator(
          `a:not([role="radio"])[href*="/search/${searchTypeName}"][href$="q=birds"]`
        )
        await expect(contentLink).toContainText(searchType.results)
        await page.click(
          `a:not([role="radio"])[href*="/search/${searchTypeName}"][href$="q=birds"]`
        )

        await expect(page).toHaveURL(searchType.url)
        await checkSearchResult(page, searchType)
      })
    }
  })
})
