import { expect, test, type Page } from "@playwright/test"

import { searchFromHeader } from "~~/test/playwright/utils/navigation"

test.describe.configure({ mode: "parallel" })

test.beforeEach(async ({ page }) => {
  // We are first navigating to search because the recent searches feature has
  // not yet been implemented on the homepage.
  await page.goto("/search?q=galah")
})

const executeSearches = async (page: Page) => {
  const searches = ["honey", "galah"] // in that order
  for (const term of searches) {
    await searchFromHeader(page, term)
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
  searches.reverse().forEach((term, idx) => {
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
    .locator('[id="option-1"]')
    .click()
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
  const recentSearchesText = await page
    .locator('[data-testid="recent-searches"]')
    .textContent()
  expect(recentSearchesText).toContain("No recent searches to show.")
})
