import { expect, test } from "@playwright/test"

import {
  changeSearchType,
  goToSearchTerm,
  preparePageForTests,
  searchFromHeader,
} from "~~/test/playwright/utils/navigation"
import { mockProviderApis } from "~~/test/playwright/utils/route"

import breakpoints from "~~/test/playwright/utils/breakpoints"

import { getHeaderSearchbar } from "~~/test/playwright/utils/components"

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
 * 6. Can fetch sensitive results by toggling the UI.
 * All of these tests test search page on the client
 */

test.describe.configure({ mode: "parallel" })

test.describe("search query on CSR", () => {
  breakpoints.describeMobileAndDesktop(({ breakpoint }) => {
    test.beforeEach(async ({ context, page }) => {
      await mockProviderApis(context)
      await preparePageForTests(page, breakpoint)
    })

    test("q query parameter is set as the search term", async ({ page }) => {
      await goToSearchTerm(page, "cat", { mode: "CSR" })

      await expect(getHeaderSearchbar(page)).toHaveValue("cat")
      await expect(page).toHaveURL("search?q=cat")
    })

    test("selecting `audio` on homepage, you can search for audio", async ({
      page,
    }) => {
      await goToSearchTerm(page, "cat", { searchType: AUDIO, mode: "CSR" })

      await expect(getHeaderSearchbar(page)).toHaveValue("cat")

      await expect(page).toHaveURL("search/audio?q=cat")
    })

    test("url filter parameters not used by current mediaType are discarded", async ({
      page,
    }) => {
      await goToSearchTerm(page, "cat", {
        searchType: IMAGE,
        query: "category=photograph",
      })

      await changeSearchType(page, AUDIO)
      await expect(page).toHaveURL("/search/audio?q=cat")
    })

    test("url filter types not used by current mediaType are discarded", async ({
      page,
    }) => {
      await goToSearchTerm(page, "cat", {
        searchType: IMAGE,
        query: "aspect_ratio=tall",
      })

      await changeSearchType(page, AUDIO)
      await expect(page).toHaveURL("/search/audio?q=cat")
    })

    test("can search for a different term", async ({ page }) => {
      await goToSearchTerm(page, "cat", { searchType: IMAGE })

      await searchFromHeader(page, "dog")

      await expect(page).toHaveURL("/search/image?q=dog")
    })

    test("search for a different term keeps query parameters", async ({
      page,
    }) => {
      await goToSearchTerm(page, "cat", {
        searchType: IMAGE,
        query: "license=by&extension=jpg",
      })
      await searchFromHeader(page, "dog")

      await expect(page).toHaveURL(
        "/search/image?q=dog&license=by&extension=jpg"
      )
    })
  })
})
