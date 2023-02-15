import { test, expect } from "@playwright/test"

import {
  closeFilters,
  closeMobileMenu,
  goToSearchTerm,
  isMobileMenuOpen,
  openContentTypes,
  openFilters,
} from "~~/test/playwright/utils/navigation"
import breakpoints from "~~/test/playwright/utils/breakpoints"

test.describe.configure({ mode: "parallel" })

test.describe("mobile menu", () => {
  breakpoints.describeSm(() => {
    test("Can open filters menu on mobile at least twice", async ({ page }) => {
      await page.goto("/search/?q=cat")

      await openFilters(page)
      expect(await isMobileMenuOpen(page)).toBe(true)
      await closeFilters(page)

      await openFilters(page)
      expect(await isMobileMenuOpen(page)).toBe(true)
      await closeFilters(page)
      expect(await isMobileMenuOpen(page)).toBe(false)
    })

    test("Can open mobile menu at least twice", async ({ page }) => {
      await goToSearchTerm(page, "cat")
      await openContentTypes(page)
      expect(await isMobileMenuOpen(page)).toBe(true)
      await closeMobileMenu(page)

      await openContentTypes(page)
      expect(await isMobileMenuOpen(page)).toBe(true)
      await closeMobileMenu(page)
      expect(await isMobileMenuOpen(page)).toBe(false)
    })
  })
})
