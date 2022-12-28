import { test, Page } from "@playwright/test"

import breakpoints from "~~/test/playwright/utils/breakpoints"
import { hideInputCursors } from "~~/test/playwright/utils/page"
import {
  dismissTranslationBanner,
  pathWithDir,
  languageDirections,
  enableNewHeader,
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

/**
 * Make the random set of images uniform by dropping their brightness to zero,
 * and changing them into black circles.
 */
const cleanImageCarousel = async (page: Page) => {
  await page.addStyleTag({
    content: ".home-cell > img { filter: brightness(0%); }",
  })
  await page.waitForTimeout(1000) // wait for animation to finish
}

for (const dir of languageDirections) {
  test.describe(`${dir} homepage snapshots`, () => {
    const path = pathWithDir("/", dir)
    test.beforeEach(async ({ page }) => {
      await page.goto(path)
      await dismissTranslationBanner(page)
      // TODO: Remove this after the cookie-based layout is merged.
      await page.waitForLoadState("networkidle")
    })

    breakpoints.describeEvery(({ expectSnapshot }) =>
      test(`${dir} full page old design`, async ({ page }) => {
        await deleteImageCarousel(page)
        await expectSnapshot(`index-old-design-${dir}`, page)
      })
    )

    breakpoints.describeEvery(({ expectSnapshot }) =>
      test(`${dir} full page`, async ({ page }) => {
        await enableNewHeader(page)
        await page.reload() // to show the redesigned page
        await cleanImageCarousel(page)
        await expectSnapshot(`index-${dir}`, page)
      })
    )

    test.describe("search input", () => {
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
