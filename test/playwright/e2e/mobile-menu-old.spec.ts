import { expect, test } from "@playwright/test"

import {
  closeMobileMenu,
  enableOldHeader,
  goToSearchTerm,
  OLD_HEADER,
  openContentTypes,
  openFilters,
} from "~~/test/playwright/utils/navigation"

const mockUaString =
  "Mozilla/5.0 (Android 7.0; Mobile; rv:54.0) Gecko/54.0 Firefox/54.0"
const mobileFixture = {
  viewport: { width: 640, height: 700 },
  userAgent: mockUaString,
}
test.use(mobileFixture)

test.describe.configure({ mode: "parallel" })

test("Can open filters menu on mobile at least twice", async ({ page }) => {
  await enableOldHeader(page)
  await page.goto("/search/?q=cat")

  await openFilters(page, OLD_HEADER)
  await expect(page.locator(`input[type="checkbox"]`)).toHaveCount(11, {
    timeout: 100,
  })
  await closeMobileMenu(page, OLD_HEADER)
  await expect(page.locator(`input[type="checkbox"]`)).toHaveCount(0, {
    timeout: 100,
  })

  await openFilters(page, OLD_HEADER)
  await expect(page.locator(`input[type="checkbox"]`)).toHaveCount(11, {
    timeout: 100,
  })
})

test("Can open mobile menu at least twice", async ({ page }) => {
  await enableOldHeader(page)
  await goToSearchTerm(page, "cat")
  await openContentTypes(page, OLD_HEADER)
  await expect(page.locator("button", { hasText: "Close" })).toBeVisible()
  await closeMobileMenu(page, OLD_HEADER)
  await expect(page.locator("button", { hasText: "Close" })).not.toBeVisible()
  await openContentTypes(page, OLD_HEADER)
  await expect(page.locator("button", { hasText: "Close" })).toBeVisible()
})

test("Selecting a search type closes the modal", async ({ page }) => {
  await enableOldHeader(page)
  await goToSearchTerm(page, "cat", { headerMode: OLD_HEADER })
  await openContentTypes(page, OLD_HEADER)
  await expect(page.locator("button", { hasText: "Close" })).toBeVisible()
  await page.locator('a[role="radio"]:has-text("Audio")').click()

  await expect(page.locator("button", { hasText: "Close" })).not.toBeVisible()
})
