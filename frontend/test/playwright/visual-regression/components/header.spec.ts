import { test } from "@playwright/test"

import breakpoints, {
  isMobileBreakpoint,
} from "~~/test/playwright/utils/breakpoints"
import { hideInputCursors } from "~~/test/playwright/utils/page"
import {
  dismissAnalyticsBanner,
  filters,
  goToSearchTerm,
  languageDirections,
  preparePageForTests,
  scrollToBottom,
  sleep,
} from "~~/test/playwright/utils/navigation"

test.describe.configure({ mode: "parallel" })

const headerSelector = ".main-header"

for (const dir of languageDirections) {
  test.describe(`header-${dir}`, () => {
    breakpoints.describeEvery(({ breakpoint, expectSnapshot }) => {
      test.beforeEach(async ({ page }) => {
        await preparePageForTests(page, breakpoint, { dismissFilter: false })

        await goToSearchTerm(page, "birds", { dir })
        await dismissAnalyticsBanner(page)
      })

      test("filters open", async ({ page }) => {
        await page.mouse.move(0, 150)
        await expectSnapshot(
          `filters-open-${dir}`,
          page.locator(headerSelector)
        )
      })

      test.describe("starting with closed filters", () => {
        test.beforeEach(async ({ page }) => {
          // By default, filters are open on desktop. We need to close them.
          if (!isMobileBreakpoint(breakpoint)) {
            await filters.close(page)
          }
        })

        test("resting", async ({ page }) => {
          // Make sure the header is not hovered on
          await page.mouse.move(0, 150)
          await expectSnapshot(`resting-${dir}`, page.locator(headerSelector))
        })

        test("scrolled", async ({ page }) => {
          await scrollToBottom(page)
          await page.mouse.move(0, 150)
          await sleep(200)
          await expectSnapshot(`scrolled-${dir}`, page.locator(headerSelector))
        })

        test("searchbar hovered", async ({ page }) => {
          await page.hover("input")
          await hideInputCursors(page)
          await expectSnapshot(
            `searchbar-hovered-${dir}`,
            page.locator(headerSelector)
          )
        })

        test("searchbar active", async ({ page }) => {
          await hideInputCursors(page)
          await page.click("input")
          // Search takes up the entire view on mobile
          // But on desktop, to reduce the snapshot size, we can scope the
          // locator just to the header
          // eslint-disable-next-line playwright/no-conditional-in-test
          const locator = isMobileBreakpoint(breakpoint)
            ? page
            : page.locator(headerSelector)
          await expectSnapshot(`searchbar-active-${dir}`, locator)
        })
      })
    })
  })
}
