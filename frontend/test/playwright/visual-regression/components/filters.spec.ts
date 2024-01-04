import { test } from "@playwright/test"

import {
  filters,
  languageDirections,
  pathWithDir,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"
import breakpoints from "~~/test/playwright/utils/breakpoints"

import type { Breakpoint } from "~/constants/screens"

test.describe.configure({ mode: "parallel" })

const getFiltersName = (breakpoint: Breakpoint) =>
  breakpoint === "lg" ? "filters-sidebar" : "filters-modal"

for (const dir of languageDirections) {
  breakpoints.describeEachBreakpoint(["xs", "sm", "md", "lg"])(
    ({ breakpoint, expectSnapshot }) => {
      const isDesktop = breakpoint === "lg"
      test.beforeEach(async ({ page }) => {
        await preparePageForTests(page, breakpoint)
        await page.goto(pathWithDir("/search/?q=birds", dir))
        await filters.open(page, dir)
      })
      test(`Filters modal none selected - ${dir}`, async ({ page }) => {
        const snapshotName = `${getFiltersName(breakpoint)}-${dir}`

        await expectSnapshot(
          snapshotName,
          isDesktop ? page.locator(".sidebar") : page
        )
      })

      test(`Filters modal 1 filter selected - ${dir}`, async ({ page }) => {
        await page.locator('input[type="checkbox"]').first().check()

        const snapshotName = `${getFiltersName(breakpoint)}-checked-${dir}`

        await expectSnapshot(
          snapshotName,
          isDesktop ? page.locator(".sidebar") : page
        )
      })
    }
  )
}
