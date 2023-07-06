import { test } from "@playwright/test"

import {
  closeFiltersUsingCookies,
  dismissBannersUsingCookies,
  goToSearchTerm,
  languageDirections,
  setBreakpointCookie,
} from "~~/test/playwright/utils/navigation"
import breakpoints from "~~/test/playwright/utils/breakpoints"

import { supportedSearchTypes } from "~/constants/media"

test.describe.configure({ mode: "parallel" })
test.describe.configure({ retries: 2 })

for (const searchType of supportedSearchTypes) {
  for (const dir of languageDirections) {
    breakpoints.describeEvery(({ breakpoint, expectSnapshot }) => {
      test(`No results ${searchType} ${dir} page snapshots`, async ({
        page,
      }) => {
        await dismissBannersUsingCookies(page)
        await closeFiltersUsingCookies(page)
        await setBreakpointCookie(page, breakpoint)

        await goToSearchTerm(page, "querywithnoresults", { dir, searchType })

        // Because of the overflow scroll, we cannot use `fullPage` screenshots.
        // Instead, we set the viewport to the full height of the page content.
        const viewportHeight = await page.evaluate(() => {
          const headerElHeight =
            document.querySelector(".header-el")?.clientHeight ?? 0

          // Get the height of the children of the "#main-page" element
          const mainPageChildren =
            document.getElementById("main-page")?.children ?? []
          const childHeight = Array.from(mainPageChildren).reduce(
            (acc, child) => acc + child.clientHeight,
            0
          )
          return childHeight + headerElHeight
        })

        const viewportWidth = page.viewportSize()?.width
        await page.setViewportSize({
          width: viewportWidth ?? 0,
          height: viewportHeight + 1,
        })

        await expectSnapshot(`no-results-${searchType}-${dir}`, page)
      })
    })
  }
}
