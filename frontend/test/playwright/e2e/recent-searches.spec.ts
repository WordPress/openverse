import { expect, test, type Page } from "@playwright/test"

import {
  goToSearchTerm,
  preparePageForTests,
  searchFromHeader,
} from "~~/test/playwright/utils/navigation"
import { getH1 } from "~~/test/playwright/utils/components"

test.describe.configure({ mode: "parallel" })

test.beforeEach(async ({ page }) => {
  await preparePageForTests(page, "xl")
  // We are first navigating to search because the recent searches feature has
  // not yet been implemented on the homepage.
  await goToSearchTerm(page, "galah")
})

const executeSearches = async (page: Page) => {
  const searches = ["honey", "galah"] // in that order
  for (const term of searches) {
    await searchFromHeader(page, term)
    await expect(getH1(page, new RegExp(term, "i"))).toBeVisible()
  }
  return searches
}

test("shows recent searches in reverse chronological order", async ({
  page,
}) => {
  const searches = await executeSearches(page)
  const recentList = await page
    .locator(`[aria-label="Recent searches"]`)
    .locator('[role="option"]')
    .allTextContents()
  const searchesWithoutCurrent = searches.slice(0, -1)
  searchesWithoutCurrent.reverse().forEach((term, idx) => {
    expect(recentList[idx].trim()).toEqual(term)
  })
})

test("clicking takes user to that search", async ({ page }) => {
  await executeSearches(page)
  expect(page.url()).toContain("?q=galah")
  // Click on the input to open the Recent searches
  await page.locator('input[type="search"]').click()
  await page
    .locator(`[aria-label="Recent searches"]`)
    .getByRole("option", { name: "honey" })
    .click()
  await expect(getH1(page, /honey/i)).toBeVisible()
  expect(page.url()).toContain("?q=honey")
})

test("recent searches shows message when blank", async ({ page }) => {
  // Click on the input to open the Recent searches
  await page.locator('input[type="search"]').click()

  const recentSearchesText = await page
    .locator('[data-testid="recent-searches"]')
    .textContent()
  expect(recentSearchesText).toContain("No recent searches to show.")
})

test("clicking Clear clears the recent searches", async ({ page }) => {
  await executeSearches(page)
  // Click on the input to open the Recent searches
  await page.locator('input[type="search"]').click()
  await page.locator('[aria-label="Clear recent searches"]').click()
  await expect(
    page.locator('[aria-label="Clear recent searches"]')
  ).toBeHidden()
  const recentSearchesText = await page
    .locator('[data-testid="recent-searches"]')
    .textContent()
  expect(recentSearchesText).toContain("No recent searches to show.")
})
