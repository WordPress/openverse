import { expect, test, type Page } from "@playwright/test"

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
}

for (const dir of languageDirections) {
  breakpoints.describeEachBreakpoint(["xs", "sm", "md", "lg"])(
    ({ breakpoint, expectSnapshot }) => {
      const isDesktop = breakpoint === "lg"
      test.beforeEach(async ({ page }) => {
        await preparePageForTests(page, breakpoint)
        await goToSearchTerm(page, "birds", { dir })
        await filters.open(page, dir)
      })
      test(`filters none selected - ${dir}`, async ({ page }) => {
        await checkModalRendered(page, isDesktop, dir)

        await expectSnapshot(
          page,
          getFiltersName(breakpoint),
          isDesktop ? page.locator(".sidebar") : page,
          {
            dir,
            snapshotOptions: { maxDiffPixels: 2, maxDiffPixelRatio: undefined },
          }
        )
      })

      test(`filters 1 filter selected - ${dir}`, async ({ page }) => {
        const firstFilter = page.getByRole("checkbox").first()
        await firstFilter.check()
        await checkModalRendered(page, isDesktop, dir)

        const snapshotName = `${getFiltersName(breakpoint)}-checked`

        await firstFilter.hover()
        await expectSnapshot(
          page,
          snapshotName,
          isDesktop ? page.locator(".sidebar") : page,
          {
            dir,
            snapshotOptions: { maxDiffPixels: 2, maxDiffPixelRatio: undefined },
          }
        )
      })
    }
  )
}
