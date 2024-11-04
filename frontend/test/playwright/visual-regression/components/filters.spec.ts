import { expect, type Page } from "@playwright/test"

import { test } from "~~/test/playwright/utils/test"

import {
  filters,
  goToSearchTerm,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"
import breakpoints from "~~/test/playwright/utils/breakpoints"

import {
  type LanguageDirection,
  languageDirections,
  t,
} from "~~/test/playwright/utils/i18n"

import type { Breakpoint } from "~/constants/screens"

test.describe.configure({ mode: "parallel" })

const getFiltersName = (breakpoint: Breakpoint) =>
  breakpoint === "lg" ? "filters-sidebar" : "filters-modal"

const checkModalRendered = async (
  page: Page,
  isDesktop: boolean,
  dir: LanguageDirection
) => {
  if (isDesktop) {
    return true
  }
  const seeResultsButton = page.getByRole("button", {
    name: t("header.seeResults", dir),
  })
  await expect(seeResultsButton).toBeEnabled()
  await expect(page.getByText(t("header.loading", dir))).toBeHidden()
}

const snapshotOptions = { maxDiffPixels: 2, maxDiffPixelRatio: undefined }

for (const dir of languageDirections) {
  breakpoints.describeEachBreakpoint(["xs", "sm", "md", "lg"])(
    ({ breakpoint, expectSnapshot }) => {
      const isDesktop = breakpoint === "lg"
      const filterLocator = isDesktop ? "complementary" : "dialog"
      test.beforeEach(async ({ page }) => {
        await preparePageForTests(page, breakpoint)
      })
      test(`filters none selected - ${dir}`, async ({ page }) => {
        await goToSearchTerm(page, "birds", { dir })
        await filters.open(page, dir)
        await checkModalRendered(page, isDesktop, dir)

        await expectSnapshot(
          page,
          getFiltersName(breakpoint),
          page.getByRole(filterLocator),
          { dir, snapshotOptions }
        )
      })

      test(`filters 1 filter selected - ${dir}`, async ({ page }) => {
        await goToSearchTerm(page, "birds", {
          dir,
          query: "license_type=commercial",
        })
        await filters.open(page, dir)

        await checkModalRendered(page, isDesktop, dir)

        await expectSnapshot(
          page,
          `${getFiltersName(breakpoint)}-checked`,
          page.getByRole(filterLocator),
          { dir, snapshotOptions }
        )
      })
    }
  )
}
