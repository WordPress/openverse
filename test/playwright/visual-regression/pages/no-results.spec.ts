import { test } from "@playwright/test"

import {
  enableNewHeader,
  goToSearchTerm,
  languageDirections,
  setCookies,
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
        await enableNewHeader(page)
        await setCookies(page.context(), {
          uiBreakpoint: breakpoint as string,
          uiIsFilterDismissed: true,
          uiDismissedBanners: ["translation-ar"],
        })
        await goToSearchTerm(page, "querywithnoresults", { dir, searchType })

        await expectSnapshot(`no-results-${searchType}-${dir}`, page, {
          fullPage: true,
        })
      })
    })
  }
}
