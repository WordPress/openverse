import { test } from "@playwright/test"

import {
  goToSearchTerm,
  languageDirections,
  t,
} from "~~/test/playwright/utils/navigation"

import breakpoints from "~~/test/playwright/utils/breakpoints"

import { supportedSearchTypes } from "~/constants/media"

test.describe.configure({ mode: "parallel" })

for (const dir of languageDirections) {
  for (const searchType of supportedSearchTypes) {
    breakpoints.describeMobileAndDesktop(async ({ expectSnapshot }) => {
      test(`External ${searchType} sources popover - ${dir}`, async ({
        page,
      }) => {
        await goToSearchTerm(page, "birds", { searchType, dir })

        const externalSourcesButton = page.getByRole("button", {
          name: t("externalSources.button", dir),
        })

        await page
          .getByRole("contentinfo")
          .getByRole("link", { name: "Openverse" })
          .scrollIntoViewIfNeeded()

        await externalSourcesButton.click()
        await page.mouse.move(0, 0)

        await expectSnapshot(
          `external-${searchType}-sources-popover-${dir}`,
          page.getByRole("dialog"),
          {},
          { maxDiffPixelRatio: 0.01 }
        )
      })
    })
  }
}
