import { test, Page } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"
import { hideInputCursors } from "~~/test/playwright/utils/page"
import {
  dismissTranslationBanner,
  pathWithDir,
  languageDirections,
  enableOldHeader,
} from "~~/test/playwright/utils/navigation"

test.describe.configure({ mode: "parallel" })

/**
 * Remove the randomly-selected images from the homepage.
 */
const deleteImageCarousel = async (page: Page) => {
  const element = await page.$('[data-testid="image-carousel"]')
  await element?.evaluate((node) => node.remove())
  element?.dispose()
}

for (const dir of languageDirections) {
  test.describe(`${dir} homepage snapshots`, () => {
    const path = pathWithDir("/", dir)
    test.beforeEach(async ({ page }) => {
      await enableOldHeader(page)
      await page.goto(path)
      await dismissTranslationBanner(page)
      await deleteImageCarousel(page)
    })

    breakpoints.describeEvery(({ expectSnapshot }) =>
      test(`${dir} full page old design`, async ({ page }) => {
        await expectSnapshot(`index-${dir}`, page)
      })
    )

    test.describe("search input", () => {
      breakpoints.describeEachDesktopWithMd(({ expectSnapshot }) => {
        test("content switcher open", async ({ page }) => {
          await page
            .locator("[aria-controls='content-switcher-popover']")
            .click()

          await expectSnapshot(`content-switcher-open-${dir}`, page)
        })
      })

      breakpoints.describeEvery(({ expectSnapshot }) => {
        test("unfocused", async ({ page }) => {
          await expectSnapshot(
            `unfocused-search-${dir}`,
            page.locator("form:has(input)")
          )
        })

        test("focused", async ({ page }) => {
          await page.focus("input")
          await hideInputCursors(page)
          await expectSnapshot(
            `focused-search-${dir}`,
            page.locator("form:has(input)")
          )
        })
      })
    })
  })
}
