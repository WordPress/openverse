import { expect } from "@playwright/test"
import { test } from "~~/test/playwright/utils/test"
import breakpoints from "~~/test/playwright/utils/breakpoints"
import {
  pathWithDir,
  preparePageForTests,
} from "~~/test/playwright/utils/navigation"
import { languageDirections, t } from "~~/test/playwright/utils/i18n"
import {
  getH1,
  getHomepageSearchButton,
  getLanguageSelect,
  getLoadMoreButton,
  getThemeSwitcher,
} from "~~/test/playwright/utils/components"

test.describe.configure({ mode: "parallel" })

const contentPages = {
  about: "about",
  privacy: "privacy",
  "search-help": "searchGuide",
  sources: "sources",
  "sensitive-content": "sensitive",
}

for (const [contentPage, title] of Object.entries(contentPages)) {
  for (const dir of languageDirections) {
    test.describe(`${contentPage} ${dir} page snapshots`, () => {
      breakpoints.describeEvery(({ breakpoint, expectSnapshot }) => {
        test("full page", async ({ page }) => {
          await preparePageForTests(page, breakpoint)

          await page.goto(pathWithDir(contentPage, dir))
          // Ensure the page is hydrated
          await expect(getH1(page, t(`${title}.title`, dir))).toBeVisible()
          await expect(getThemeSwitcher(page, dir)).toHaveValue("system")

          // Make sure header is not hovered on
          await page.mouse.move(150, 150)
          await expectSnapshot(page, contentPage, page, {
            dir,
            screenshotOptions: { fullPage: true },
          })
        })
      })
    })
  }
}

test.describe("layout color is set correctly", () => {
  breakpoints.describeLg(() => {
    test.beforeEach(async ({ page }) => {
      await preparePageForTests(page, "lg", { dismissFilter: false })
    })

    test("change language on homepage and search", async ({ page }) => {
      await page.goto("/")

      const searchButton = getHomepageSearchButton(page)
      const languageSelect = getLanguageSelect(page)

      // Wait for hydration
      await expect(searchButton).toBeEnabled()

      await expect(languageSelect).toHaveValue("en")
      await languageSelect.selectOption("ar")

      await page.waitForURL(/ar/)

      const searchBar = page.getByRole("searchbox")
      await searchBar.fill("cat")
      await searchBar.press("Enter")

      await page.waitForURL(/ar\/search/)
      await expect(getH1(page, "Cat")).toBeVisible()
      await expect(getLoadMoreButton(page, "rtl")).toBeEnabled()

      expect(await page.screenshot()).toMatchSnapshot(
        "search-page-rtl-lg-light.png"
      )
    })

    test("change language on homepage and go to content page", async ({
      page,
    }) => {
      await page.goto("/ar")

      const searchButton = getHomepageSearchButton(page, "rtl")
      const languageSelect = getLanguageSelect(page, "rtl")

      // Wait for hydration
      await expect(searchButton).toBeEnabled()
      await languageSelect.selectOption("en")

      await page
        .getByRole("link", { name: t("navigation.about", "ltr") })
        .click()

      await page.waitForURL(/about/)
      await expect(getH1(page, t("about.title"))).toBeVisible()
      await page.mouse.move(100, 100)

      expect(await page.screenshot({ fullPage: true })).toMatchSnapshot(
        "about-ltr-lg-light.png"
      )
    })
  })
})
