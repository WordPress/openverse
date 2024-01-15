import { test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"
import {
  goToSearchTerm,
  preparePageForTests,
  sleep,
} from "~~/test/playwright/utils/navigation"

import { setViewportToFullHeight } from "~~/test/playwright/utils/viewport"

import { languageDirections } from "~~/test/playwright/utils/i18n"

import { ALL_MEDIA, supportedSearchTypes } from "~/constants/media"

test.describe.configure({ mode: "parallel" })

// Tapes for simulating server single result errors.
const errorTapes = [
  { errorStatus: 500, imageId: "da5cb478-c093-4d62-b721-cda18797e3fe" },
]
const singleResultCSRErrorStatuses = [404, 429, 500]
/**
 * SINGLE RESULT PAGE ERRORS
 */
breakpoints.describeXl(({ breakpoint, expectSnapshot }) => {
  for (const { errorStatus, imageId } of errorTapes) {
    test(`${errorStatus} error on single-result image page on SSR`, async ({
      page,
    }) => {
      await preparePageForTests(page, breakpoint)

      await page.goto(`/image/${imageId}`)
      // eslint-disable-next-line playwright/no-networkidle
      await page.waitForLoadState("networkidle")
      await expectSnapshot("generic-error", page, { fullPage: true })
    })
  }

  for (const status of singleResultCSRErrorStatuses) {
    test(`${status} on single-result image page on CSR`, async ({ page }) => {
      await page.route(new RegExp(`v1/images/`), (route) => {
        return route.fulfill({ status })
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

      await expectSnapshot("generic-error", page, { fullPage: true })
    })
  }
})

/**
 * SEARCH PAGE ERRORS
 *
 * On SSR, we only test for 500.
 * We can't test 404 errors because when there are no results, the server returns
 * a 200 response with an empty list as the `results`.
 * The server uses a throttle-exempt key, so we can't get 429 errors.
 */
for (const searchType of supportedSearchTypes) {
  breakpoints.describeXl(({ breakpoint, expectSnapshot }) => {
    test(`500 error on ${searchType} search on SSR`, async ({ page }) => {
      await preparePageForTests(page, breakpoint)
      await goToSearchTerm(page, `SearchPage500error`, { searchType })

      await expectSnapshot("generic-error", page, {
        fullPage: true,
      })
    })
  })
}

const searchCSRErrorStatuses = [429, 500]

for (const searchType of supportedSearchTypes) {
  breakpoints.describeMobileAndDesktop(({ breakpoint, expectSnapshot }) => {
    test.beforeEach(async ({ page }) => {
      await preparePageForTests(page, breakpoint)
    })
    for (const dir of languageDirections) {
      for (const errorStatus of searchCSRErrorStatuses) {
        test(`${errorStatus} error on ${dir} ${searchType} search on CSR`, async ({
          page,
        }) => {
          await goToSearchTerm(page, `SearchPage${errorStatus}error`, {
            mode: "CSR",
            searchType,
          })

          await expectSnapshot("generic-error", page, { fullPage: true })
        })
      }

      test(`no results ${searchType} ${dir} page snapshots`, async ({
        page,
      }) => {
        await goToSearchTerm(page, "querywithnoresults", { dir, searchType })
        await sleep(500)

        await setViewportToFullHeight(page)

        await page.mouse.move(0, 82)

        await expectSnapshot(
          `search-result-${
            searchType === ALL_MEDIA ? "image" : searchType
          }-no-results-${dir}`,
          page.locator("#main-page")
        )
      })

      test(`timeout ${searchType} ${dir} page snapshots`, async ({ page }) => {
        await page.route(new RegExp(`/v1/(images|audio)/`), async (route) => {
          return route.abort("timedout")
        })
        await goToSearchTerm(page, "cat", { dir, searchType, mode: "CSR" })

        await setViewportToFullHeight(page)

        await page.mouse.move(0, 82)

        await expectSnapshot(
          `search-result-timeout-${dir}`,
          page.locator("#main-page")
        )
      })
    }
  })
}
