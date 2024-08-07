import { expect, test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"
import {
  pathWithDir,
  preparePageForTests,
  sleep,
} from "~~/test/playwright/utils/navigation"
import { languageDirections, t } from "~~/test/playwright/utils/i18n"
import {
  getH1,
  getHomepageSearchButton,
  getLanguageSelect,
} from "~~/test/playwright/utils/components"

test.describe.configure({ mode: "parallel" })

const contentPages = [
  "about",
  "privacy",
  "search-help",
  // "non-existent", TODO: re-add dir properties to error page
  "sources",
  "sensitive-content",
]
for (const contentPage of contentPages) {
  for (const dir of languageDirections) {
    test.describe(`${contentPage} ${dir} page snapshots`, () => {
      breakpoints.describeEvery(({ breakpoint, expectSnapshot }) => {
        test("full page", async ({ page }) => {
          await preparePageForTests(page, breakpoint)

          await page.goto(pathWithDir(contentPage, dir))
          // Make sure header is not hovered on
          await page.mouse.move(150, 150)
          await expectSnapshot(
            `${contentPage}-${dir}`,
            page,
            {
              fullPage: true,
            },
            { maxDiffPixelRatio: 0.005 }
          )
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

      expect(await page.screenshot()).toMatchSnapshot("search-page-rtl-lg.png")
    })

    test("change language on homepage and go to content page", async ({
      page,
    }) => {
      await page.goto("/ar")

      // wait for hydration
      await sleep(500)
      await getLanguageSelect(page, "rtl").selectOption("en")

      await page
        .getByRole("link", { name: t("navigation.about", "ltr") })
        .click()
      await page.mouse.move(100, 100)

      expect(await page.screenshot({ fullPage: true })).toMatchSnapshot(
        "about-ltr-lg.png",
        { maxDiffPixelRatio: 0.01 }
      )
    })
  })
})
