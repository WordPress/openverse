import { expect, test } from "@playwright/test"

import {
  changeContentType,
  goToSearchTerm,
  OLD_HEADER,
} from "~~/test/playwright/utils/navigation"
import { mockProviderApis } from "~~/test/playwright/utils/route"

import { AUDIO, IMAGE } from "~/constants/media"

/**
 * When navigating to the search page on the client side:
 * 1. `q` parameter is set as the search input value and url parameter.
 * 2. Selecting 'audio' on homepage sets the search page path and search tab.
 * 3. Selecting filters on the homepage sets the search query and url parameter.
 * 4. Query parameters (filter types or filter values) that are not used for
 * current media type are discarded.
 * 5. Can change the `q` parameter by typing into the search input and clicking on
 * the Search button.
 * All of these tests test search page on the client
 */

test.describe.configure({ mode: "parallel" })

test.beforeEach(async ({ context }) => {
  await mockProviderApis(context)
})

test("q query parameter is set as the search term", async ({ page }) => {
  await goToSearchTerm(page, "cat", { mode: "CSR" })

  await expect(page.locator('header input[type="search"]')).toHaveValue("cat")
  await expect(page).toHaveURL("search/?q=cat")
})

test("selecting `audio` on homepage, you can search for audio", async ({
  page,
}) => {
  await goToSearchTerm(page, "cat", {
    searchType: AUDIO,
    mode: "CSR",
    headerMode: OLD_HEADER,
  })

  await expect(page.locator('header input[type="search"]')).toHaveValue("cat")

  await expect(page).toHaveURL("search/audio?q=cat")
})

test("url filter parameters not used by current mediaType are discarded", async ({
  page,
}) => {
  await goToSearchTerm(page, "cat", {
    searchType: IMAGE,
    query: "category=photograph",
    headerMode: OLD_HEADER,
  })

  await changeContentType(page, "Audio", OLD_HEADER)
  await expect(page).toHaveURL("/search/audio?q=cat")
})

test("url filter types not used by current mediaType are discarded", async ({
  page,
}) => {
  await goToSearchTerm(page, "cat", {
    searchType: IMAGE,
    query: "aspect_ratio=tall",
    headerMode: OLD_HEADER,
  })

  await changeContentType(page, "Audio", OLD_HEADER)
  await expect(page).toHaveURL("/search/audio?q=cat")
})

test("can search for a different term", async ({ page }) => {
  await goToSearchTerm(page, "cat", {
    searchType: IMAGE,
    headerMode: OLD_HEADER,
  })
  await page.fill('header input[type="search"]', "dog")
  await page.keyboard.press("Enter")
  await expect(page).toHaveURL("/search/image?q=dog")
})

test("search for a different term keeps query parameters", async ({ page }) => {
  await goToSearchTerm(page, "cat", {
    searchType: IMAGE,
    query: "license=by&extension=jpg",
    headerMode: OLD_HEADER,
  })
  await page.fill('header input[type="search"]', "dog")
  await page.keyboard.press("Enter")
  await expect(page).toHaveURL("/search/image?q=dog&license=by&extension=jpg")
})
