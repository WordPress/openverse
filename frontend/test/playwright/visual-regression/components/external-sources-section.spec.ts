import { test } from "@playwright/test"

import {
  goToSearchTerm,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"

import breakpoints from "~~/test/playwright/utils/breakpoints"

import { languageDirections, t } from "~~/test/playwright/utils/i18n"

import { supportedMediaTypes } from "~/constants/media"

test.describe.configure({ mode: "parallel" })

for (const dir of languageDirections) {
  for (const mediaType of supportedMediaTypes) {
    breakpoints.describeMobileAndDesktop(
      async ({ breakpoint, expectSnapshot }) => {
        test(`external ${mediaType} sources popover - ${dir}`, async ({
          page,
        }) => {
          await preparePageForTests(page, breakpoint)

          await goToSearchTerm(page, "birds", { searchType: mediaType, dir })

          const externalSourcesButton = page.getByRole("button", {
            name: new RegExp(
              t("externalSources.form.supportedTitleSm", dir),
              "i"
            ),
          })

          await page
            .getByRole("contentinfo")
            .getByRole("link", { name: "Openverse" })
            .scrollIntoViewIfNeeded()

          await externalSourcesButton.click()
          await page.mouse.move(0, 0)

          await expectSnapshot(
            `external-${mediaType}-sources-popover-${dir}`,
            page.getByRole("dialog"),
            {},
            { maxDiffPixelRatio: 0.01, maxDiffPixels: undefined }
          )
        })
      }
    )
  }
}
