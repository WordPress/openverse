import { expect, test, type Page } from "@playwright/test"

import {
  goToSearchTerm,
  preparePageForTests,
  searchFromHeader,
  sleep,
} from "~~/test/playwright/utils/navigation"
import { getH1 } from "~~/test/playwright/utils/components"
import { t } from "~~/test/playwright/utils/i18n"
import breakpoints from "~~/test/playwright/utils/breakpoints"

test.describe.configure({ mode: "parallel" })

const clearRecentLabel = t("recentSearches.clear.label")
const recentLabel = t("recentSearches.heading")
const noRecentLabel = t("recentSearches.none")

const getRecentSearchesText = async (page: Page) =>
  await page.locator('[data-testid="recent-searches"]').textContent()

const clearButton = async (page: Page) =>
  page.locator(`[aria-label="${clearRecentLabel}"]`)
const clickClear = async (page: Page) => (await clearButton(page)).click()

const recentSearches = (page: Page) =>
  page.locator('[data-testid="recent-searches"]')

const tabToSearchbar = async (page: Page) => {
  await page.getByRole("link", { name: t("skipToContent") }).focus()
  for (let i = 0; i < 2; i++) {
    await page.keyboard.press("Tab")
  }
}

const executeSearches = async (page: Page) => {
  const searches = ["honey", "galah"] // in that order
  for (const term of searches) {
    await searchFromHeader(page, term)
    await expect(getH1(page, new RegExp(term, "i"))).toBeVisible()
  }
  return searches
}

breakpoints.describeMobileXsAndDesktop(({ breakpoint }) => {
  test.beforeEach(async ({ page }) => {
    await preparePageForTests(page, breakpoint)
    // We are first navigating to search because the recent searches feature has
    // not yet been implemented on the homepage.
    await goToSearchTerm(page, "galah")
  })

  test("recent searches shows message when blank", async ({ page }) => {
    // Click on the input to open the Recent searches
    await page.locator('input[type="search"]').click()
    await clickClear(page)

    const recentSearchesText = await getRecentSearchesText(page)
    expect(recentSearchesText).toContain(noRecentLabel)
  })

  test("shows recent searches in reverse chronological order", async ({
    page,
  }) => {
    const searches = await executeSearches(page)
    const recentList = await page
      .locator(`[aria-label="${recentLabel}"]`)
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
      .locator(`[aria-label="${recentLabel}"]`)
      .getByRole("option", { name: "honey" })
      .click()
    await expect(getH1(page, /honey/i)).toBeVisible()
    expect(page.url()).toContain("?q=honey")
  })

  test("clicking Clear clears the recent searches", async ({ page }) => {
    await executeSearches(page)
    // Click on the input to open the Recent searches
    await page.locator('input[type="search"]').click()
    await clickClear(page)
    await expect(await clearButton(page)).toBeHidden()

    const recentSearchesText = await getRecentSearchesText(page)
    expect(recentSearchesText).toContain(noRecentLabel)
  })

  test("can open recent searches with keyboard", async ({ page }) => {
    await executeSearches(page)
    await tabToSearchbar(page)
    await page.keyboard.press("ArrowDown")

    await expect(recentSearches(page)).toBeVisible()
  })

  test("can close the recent searches with escape key", async ({ page }) => {
    await executeSearches(page)
    await tabToSearchbar(page)

    await page.keyboard.press("ArrowDown")
    await expect(recentSearches(page)).toBeVisible()

    await page.keyboard.press("Escape")
    await sleep(300)
    await expect(recentSearches(page)).toBeHidden()
  })

  test("can navigate out of the recent searches with tab key", async ({
    page,
  }) => {
    const searches = await executeSearches(page)
    await tabToSearchbar(page)

    await page.keyboard.press("ArrowDown")
    await expect(recentSearches(page)).toBeVisible()

    for (let i = 0; i < searches.length + 3; i++) {
      await page.keyboard.press("Tab")
    }
    await expect(recentSearches(page)).toBeHidden()
  })

  test("can navigate out of the recent searches using shift tab", async ({
    page,
  }) => {
    await executeSearches(page)
    await tabToSearchbar(page)

    await page.keyboard.press("ArrowDown")
    await expect(recentSearches(page)).toBeVisible()

    await page.keyboard.press("Shift+Tab")
    await page.keyboard.press("Shift+Tab")
    await expect(recentSearches(page)).toBeHidden()
  })
})
