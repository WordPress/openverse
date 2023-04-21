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

        await expectSnapshot(`no-results-${searchType}-${dir}`, page, {
          fullPage: true,
        })
      })
    })
  }
}
