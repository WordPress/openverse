import { expect, test, type Page } from "@playwright/test"

import {
  goToSearchTerm,
  isPageDesktop,
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

const searchbarName = t("search.searchBarLabel").replace(
  "{openverse}",
  "Openverse"
)

const recentSearches = (page: Page) =>
  page.locator('[data-testid="recent-searches"]')

const openRecentSearches = async (page: Page) => {
  if (!(await recentSearches(page).isVisible())) {
    await page.getByRole("combobox", { name: searchbarName }).click()
  }
}

const getFocusedElementName = async (page: Page) => {
  return await page.evaluate(() => {
    const el = document.activeElement as HTMLElement
    return el ? (el.getAttribute("aria-label") ?? el.textContent) : null
  })
}

const tabToSearchbar = async (page: Page) => {
  await page.getByRole("link", { name: t("skipToContent") }).focus()

  let focusedInputName = null
  while (focusedInputName !== searchbarName) {
    await page.keyboard.press("Tab")
    focusedInputName = await page.evaluate(() => {
      const el = document.activeElement as HTMLElement
      return el && el.nodeName === "INPUT"
        ? el.getAttribute("aria-label")
        : null
    })
  }
}

const openRecentSearchesWithKeyboard = async (page: Page) => {
  await tabToSearchbar(page)
  expect(await getFocusedElementName(page)).toEqual(searchbarName)
  await page.keyboard.press("ArrowDown")
}

const executeSearches = async (page: Page) => {
  const searches = ["honey", "galah"] // in that order
  for (const term of searches) {
    await searchFromHeader(page, term)
    await expect(getH1(page, new RegExp(term, "i"))).toBeVisible()
  }
  return searches
}

const getLastFocusableElementLabel = (page: Page, firstSearch: string) => {
  return isPageDesktop(page)
    ? clearRecentLabel
    : t("recentSearches.clearSingle.label").replace("{entry}", firstSearch)
}

breakpoints.describeMobileXsAndDesktop(({ breakpoint }) => {
  test.beforeEach(async ({ page }) => {
    await preparePageForTests(page, breakpoint)
    // We are first navigating to search because the recent searches feature has
    // not yet been implemented on the homepage.
    await goToSearchTerm(page, "galah")
  })

  test("recent searches shows message when blank", async ({ page }) => {
    await openRecentSearches(page)
    await clickClear(page)

    const recentSearchesText = await getRecentSearchesText(page)
    expect(recentSearchesText).toContain(noRecentLabel)
  })

  test("shows recent searches in reverse chronological order", async ({
    page,
  }) => {
    const searches = await executeSearches(page)
    await openRecentSearches(page)
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

    await page.waitForURL(/search\?q=galah/)

    await openRecentSearches(page)
    await page
      .locator(`[aria-label="${recentLabel}"]`)
      .getByRole("option", { name: "honey" })
      .click()

    await page.waitForURL(/search\?q=honey/)
    await expect(getH1(page, /honey/i)).toBeVisible()
  })

  test("clicking Clear clears the recent searches", async ({ page }) => {
    await executeSearches(page)
    await openRecentSearches(page)
    await clickClear(page)
    await expect(await clearButton(page)).toBeHidden()

    const recentSearchesText = await getRecentSearchesText(page)
    expect(recentSearchesText).toContain(noRecentLabel)
  })
})

breakpoints.describeMobileXsAndDesktop(({ breakpoint }) => {
  for (const dismissBanners of [true, false]) {
    test.beforeEach(async ({ page }) => {
      await preparePageForTests(page, breakpoint, { dismissBanners })
      // We are first navigating to search because the recent searches feature has
      // not yet been implemented on the homepage.
      await goToSearchTerm(page, "galah")
    })
    const bannerStatus = `${dismissBanners ? "without" : "with"} banners`

    test(`can open recent searches with keyboard, ${bannerStatus}`, async ({
      page,
    }) => {
      await executeSearches(page)

      await openRecentSearchesWithKeyboard(page)
      await expect(recentSearches(page)).toBeVisible()
    })

    test(`can close the recent searches with escape key, ${bannerStatus}`, async ({
      page,
    }) => {
      await executeSearches(page)

      await openRecentSearchesWithKeyboard(page)
      await expect(recentSearches(page)).toBeVisible()

      await page.keyboard.press("Escape")
      await sleep(300)
      await expect(recentSearches(page)).toBeHidden()
    })

    test(`can navigate out of the recent searches with tab key, ${bannerStatus}`, async ({
      page,
    }) => {
      const searches = await executeSearches(page)

      await openRecentSearchesWithKeyboard(page)

      await expect(recentSearches(page)).toBeVisible()

      const lastFocusableElementLabel = getLastFocusableElementLabel(
        page,
        searches[0]
      )

      let focused = await getFocusedElementName(page)
      while (focused !== lastFocusableElementLabel) {
        await page.keyboard.press("Tab")
        focused = await getFocusedElementName(page)
      }
      await page.keyboard.press("Tab")

      await expect(recentSearches(page)).toBeHidden()
    })

    test(`can navigate out of the recent searches using shift tab, ${bannerStatus}`, async ({
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
  }
})
