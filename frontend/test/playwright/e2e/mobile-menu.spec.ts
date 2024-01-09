import { test, expect } from "@playwright/test"

import {
  goToSearchTerm,
  isDialogOpen,
  searchTypes,
  filters,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"
import breakpoints from "~~/test/playwright/utils/breakpoints"

test.describe.configure({ mode: "parallel" })

test.describe("mobile menu", () => {
  test.beforeEach(async ({ page }) => {
    await preparePageForTests(page, "sm")
  })
  breakpoints.describeSm(() => {
    test("Can open filters menu on mobile at least twice", async ({ page }) => {
      await goToSearchTerm(page, "cat", { searchType: "all", mode: "SSR" })

      await filters.open(page)
      expect(await isDialogOpen(page)).toBe(true)
      await filters.close(page)

      await filters.open(page)
      expect(await isDialogOpen(page)).toBe(true)
      await filters.close(page)
      expect(await isDialogOpen(page)).toBe(false)
    })

    test("Can open mobile menu at least twice", async ({ page }) => {
      await goToSearchTerm(page, "cat")
      await searchTypes.open(page)
      expect(await isDialogOpen(page)).toBe(true)
      await searchTypes.close(page)

      await searchTypes.open(page)
      expect(await isDialogOpen(page)).toBe(true)
      await searchTypes.close(page)
      expect(await isDialogOpen(page)).toBe(false)
    })
  })
})
