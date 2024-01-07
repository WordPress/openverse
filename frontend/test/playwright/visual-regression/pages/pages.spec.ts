import { expect, test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"
import {
  languageDirections,
  pathWithDir,
  preparePageForTests,
  sleep,
  t,
} from "~~/test/playwright/utils/navigation"

test.describe.configure({ mode: "parallel" })

const contentPages = [
  "about",
  "privacy",
  "search-help",
  "non-existent",
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
            { maxDiffPixelRatio: 0.01 }
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

    // https://github.com/wordpress/openverse/issues/411
    test.skip("change language on homepage and search", async ({ page }) => {
      await page.goto("/")
      await page.getByRole("combobox", { name: "Language" }).selectOption("ar")
      const searchBar = page.getByPlaceholder(
        t("hero.search.placeholder", "rtl")
      )
      await searchBar.fill("cat")
      await searchBar.press("Enter")

      await expect(
        page.getByRole("heading", { level: 1, name: "Cat" })
      ).toBeVisible()
      await page.waitForURL(/ar\/search/)

      expect(await page.screenshot()).toMatchSnapshot("search-page-rtl-lg.png")
    })

    test("change language on homepage and go to content page", async ({
      page,
    }) => {
      await page.goto("/ar")

      // wait for hydration
      await sleep(500)
      await page
        .getByRole("combobox", { name: t("language.language", "rtl") })
        .selectOption("en")

      await page
        .getByRole("link", { name: t("navigation.about", "ltr") })
        .click()
      await page.mouse.move(100, 100)

      expect(await page.screenshot({ fullPage: true })).toMatchSnapshot(
        "about-ltr-lg.png",
        { maxDiffPixelRatio: 0.01 }
      )
    })

    // https://github.com/wordpress/openverse/issues/411
    test.skip("nonexistent `image` page", async ({ page }) => {
      await page.goto("/image/non-existent")

      expect(await page.screenshot({ fullPage: true })).toMatchSnapshot(
        "non-existent-ltr-lg.png",
        { maxDiffPixelRatio: 0.01 }
      )
    })
  })
})
