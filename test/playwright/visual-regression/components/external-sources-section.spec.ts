import { test } from "@playwright/test"

import {
  enableNewHeader,
  goToSearchTerm,
  languageDirections,
} from "~~/test/playwright/utils/navigation"

import breakpoints from "~~/test/playwright/utils/breakpoints"

import { supportedSearchTypes } from "~/constants/media"

test.describe.configure({ mode: "parallel" })

for (const dir of languageDirections) {
  for (const searchType of supportedSearchTypes) {
    breakpoints.describeMobileAndDesktop(
      async ({ breakpoint, expectSnapshot }) => {
        test(`External ${searchType} sources popover - ${dir}`, async ({
          page,
        }) => {
          await enableNewHeader(page)
          await goToSearchTerm(page, "birds", { searchType, dir })
          const sourcesId = `external-sources-${
            breakpoint === "xl" ? "popover" : "modal"
          }`
          const externalSourcesButton = page.locator(
            `[aria-controls="${sourcesId}"]`
          )

          await externalSourcesButton.click()

          await expectSnapshot(
            `external-${searchType}-sources-popover-${dir}.png`,
            page.locator(`#${sourcesId}`)
          )
        })
      }
    )
  }
}
