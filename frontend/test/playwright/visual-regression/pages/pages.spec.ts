import { expect, test } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"
import { removeHiddenOverflow } from "~~/test/playwright/utils/page"
import {
  closeFiltersUsingCookies,
  dismissBannersUsingCookies,
  languageDirections,
  pathWithDir,
  setBreakpointCookie,
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
      test.describe.configure({ retries: 2 })

      breakpoints.describeEvery(({ breakpoint, expectSnapshot }) => {
        test.beforeEach(async ({ page }) => {
          await dismissBannersUsingCookies(page)
          await closeFiltersUsingCookies(page)
          await setBreakpointCookie(page, breakpoint)

          await page.goto(pathWithDir(contentPage, dir))
        })

        test("full page", async ({ page }) => {
          await removeHiddenOverflow(page)
          // Make sure header is not hovered on
          await page.mouse.move(150, 150)
          await expectSnapshot(`${contentPage}-${dir}`, page, {
            fullPage: true,
          })
        })
      })
    })
  }
}

test.describe("Layout color is set correctly", () => {
  breakpoints.describeLg(() => {
    test.beforeEach(async ({ page }) => {
      await dismissBannersUsingCookies(page)
    })

    test("Change language on homepage and search", async ({ page }) => {
      await page.goto("/")
      await page.getByRole("combobox", { name: "Language" }).selectOption("ar")
      await page.getByPlaceholder("البحث عن محتوى").fill("cat")
      await page.getByRole("button", { name: "يبحث" }).click()

      await page.waitForURL(/ar\/search/)
      await expect(page.getByRole("heading", { name: "Cat" })).toBeVisible()

      expect(await page.screenshot()).toMatchSnapshot("search-page-rtl-lg.png")
    })

    test("Change language on homepage and go to content page", async ({
      page,
    }) => {
      await page.goto("/ar")
      await page.getByRole("combobox", { name: "لغة" }).selectOption("en")

      await page.getByRole("link", { name: "About" }).click()
      await page.mouse.move(100, 100)

      expect(await page.screenshot({ fullPage: true })).toMatchSnapshot(
        "about-ltr-lg.png"
      )
    })

    test("Nonexistent `image` page", async ({ page }) => {
      await page.goto("/image/non-existent")

      expect(await page.screenshot({ fullPage: true })).toMatchSnapshot(
        "non-existent-ltr-lg.png"
      )
    })
  })
})
