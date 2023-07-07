import { test } from "@playwright/test"

import breakpoints, {
  isMobileBreakpoint,
} from "~~/test/playwright/utils/breakpoints"
import { hideInputCursors } from "~~/test/playwright/utils/page"
import {
  filters,
  goToSearchTerm,
  languageDirections,
  scrollToBottom,
  setBreakpointCookie,
  sleep,
} from "~~/test/playwright/utils/navigation"

test.describe.configure({ mode: "parallel" })

const headerSelector = ".main-header"

for (const dir of languageDirections) {
  test.describe(`header-${dir}`, () => {
    breakpoints.describeEvery(({ breakpoint, expectSnapshot }) => {
      test.beforeEach(async ({ page }) => {
        await setBreakpointCookie(page, breakpoint)

        await goToSearchTerm(page, "birds", { dir })
      })

      test("filters open", async ({ page }) => {
        await page.mouse.move(0, 150)
        await expectSnapshot(
          `filters-open-${dir}`,
          page.locator(headerSelector)
        )
      })

      test("resting", async ({ page }) => {
        // By default, filters are open on desktop. We need to close them.
        if (!isMobileBreakpoint(breakpoint)) {
          await filters.close(page)
        }
        // Make sure the header is not hovered on
        await page.mouse.move(0, 150)
        await expectSnapshot(`resting-${dir}`, page.locator(headerSelector))
      })

      test("scrolled", async ({ page }) => {
        if (!isMobileBreakpoint(breakpoint)) {
          await filters.close(page)
        }
        await scrollToBottom(page)
        await page.mouse.move(0, 150)
        await sleep(200)
        await expectSnapshot(`scrolled-${dir}`, page.locator(headerSelector))
      })

      test("searchbar hovered", async ({ page }) => {
        if (!isMobileBreakpoint(breakpoint)) {
          await filters.close(page)
        }
        await page.hover("input")
        await hideInputCursors(page)
        await expectSnapshot(
          `searchbar-hovered-${dir}`,
          page.locator(headerSelector)
        )
      })

      test("searchbar active", async ({ page }) => {
        if (!isMobileBreakpoint(breakpoint)) {
          await filters.close(page)
        }
        await hideInputCursors(page)
        await page.click("input")
        const locator = isMobileBreakpoint(breakpoint)
          ? page
          : page.locator(headerSelector)
        await expectSnapshot(`searchbar-active-${dir}`, locator)
      })
    })
  })
}
