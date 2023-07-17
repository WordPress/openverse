import { test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"
import {
  goToSearchTerm,
  preparePageForTests,
  renderModes,
} from "~~/test/playwright/utils/navigation"

import { supportedSearchTypes } from "~/constants/media"

test.describe.configure({ mode: "parallel" })

const errorTapes = [
  { errorStatus: 404, imageId: "da5cb478-c093-4d62-b721-cda18797e3fc" },
  { errorStatus: 429, imageId: "da5cb478-c093-4d62-b721-cda18797e3fd" },
  { errorStatus: 500, imageId: "da5cb478-c093-4d62-b721-cda18797e3fe" },
]

for (const { errorStatus, imageId } of errorTapes) {
  breakpoints.describeXl(({ breakpoint, expectSnapshot }) => {
    test(`${errorStatus} error on single-result page on SSR`, async ({
      page,
    }) => {
      await preparePageForTests(page, breakpoint)

      const path = `/image/${imageId}`

      await page.goto(path)
      await expectSnapshot(`single-result-error`, page, { fullPage: true })
    })

    test(`${errorStatus} on single-result page on CSR`, async ({ page }) => {
      await page.route(new RegExp(`v1/images/`), (route) => {
        // const requestUrl = route.request().url()

        // if (requestUrl.includes("/thumb")) {
        //   return route.continue()
        // }
        return route.fulfill({
          status: errorStatus,
          headers: { "Access-Control-Allow-Origin": "*" },
          body: JSON.stringify({}),
        })
      })

      await preparePageForTests(page, breakpoint)

      // If we navigate from the search results page, we will already have the
      // image data in the store, and will not fetch it from the API.
      // To simulate a client side error, we need to click on the home gallery:
      // then we have to make a client-side request because we don't have any
      // data for the images in the store.
      await page.goto("/")
      await page.locator("a.home-cell").first().click()
      // We can't use `waitForURL` because it would be flaky:
      // the URL loads a skeleton page before showing the error page.
      // eslint-disable-next-line playwright/no-networkidle
      await page.waitForLoadState("networkidle")

      await expectSnapshot("single-result-error-CSR", page, { fullPage: true })
    })
  })
}

for (const { errorStatus } of errorTapes) {
  for (const searchType of supportedSearchTypes) {
    for (const renderMode of renderModes) {
      breakpoints.describeXl(({ breakpoint, expectSnapshot }) => {
        test.beforeEach(async ({ page }) => {
          await preparePageForTests(page, breakpoint)
        })
        test(`${errorStatus} error on ${searchType} search on ${renderMode}`, async ({
          page,
        }) => {
          await goToSearchTerm(page, `SearchPage${errorStatus}error`, {
            mode: renderMode,
            searchType,
          })
          await expectSnapshot(
            `search-result-${searchType}-${errorStatus}-error-${renderMode}`,
            page,
            { fullPage: true }
          )
        })
      })
    }
  }
}
